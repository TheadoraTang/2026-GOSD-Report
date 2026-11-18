#!/usr/bin/env python3
"""Rebuild an approved COSSI increment using pinned external PDFs.

The work directory and every generated PDF/font/image stay outside Git.
The approved PDF hash is an identity record, not a promise of byte-identical
reconstruction across TeX, font and PDF engine versions.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

SOURCE=Path(__file__).resolve().parent
SPEC=json.loads((SOURCE/'manifest.json').read_text())

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def pinned(value,language):
    if not value:
        raise ValueError(f'--{language}-baseline is required')
    p=Path(value).resolve()
    if not p.is_file() or sha(p)!=SPEC['inputs'][language]['sha256']:
        raise ValueError(f'Wrong or missing {language} baseline; use the SHA-256 in manifest.json')
    return p

def copy(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)

def run(script,env):
    subprocess.run([sys.executable,str(script)],check=True,env=env)

def images_by_hash(pdf,needed):
    import fitz
    found={}
    with fitz.open(pdf) as doc:
        xrefs={im[0] for page in doc for im in page.get_images() if im[0]}
        for xref in sorted(xrefs):
            img=doc.extract_image(xref)
            if not img:continue
            raw=img['image'];digest=hashlib.sha256(raw).hexdigest()
            if digest in needed:found[digest]=raw
            if set(found)==set(needed):break
    if set(found)!=set(needed):
        raise ValueError(f'Pinned PDF lacks {len(set(needed)-set(found))} required images')
    return found

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=['zh-CN','en'],required=True)
    parser.add_argument('--zh-baseline',help='Approved COSSI Chinese v1.6 PDF; also supplies unchanged logos for English')
    parser.add_argument('--en-baseline',help='Approved 156-page COSSI English v0.5 PDF')
    parser.add_argument('--output-dir',required=True,help='An external directory for the rebuilt full report and audit record')
    parser.add_argument('--xelatex-fmt',help='Optional prebuilt XeLaTeX format for constrained environments')
    args=parser.parse_args()
    zh=pinned(args.zh_baseline,'zh-CN')
    en=pinned(args.en_baseline,'en') if args.language=='en' else None
    output=Path(args.output_dir).resolve()
    repository=next((p for p in SOURCE.parents if (p/'.git').exists()),None)
    if repository and output.is_relative_to(repository):
        raise ValueError('Generated outputs must be outside the repository')
    output_names=['GOSD_2026_Essential_COSSI_zh-CN_v1.7.pdf','GOSD_2026_COSSI_EN_Full_Print_v0.6.pdf']
    if any((output/name).exists() for name in output_names):
        raise ValueError('Use a new output directory; an existing full PDF will not be overwritten')
    env=os.environ.copy()
    # Baseline TeX/font dependencies are documented; no network fetches occur.
    with tempfile.TemporaryDirectory(prefix='gosd-annual-changes-') as tmp:
        work=Path(tmp)
        zhroot=work/'report-integration-v1.7'
        enroot=work/'year-change-en-v0.1'
        integration=zhroot if args.language=='zh-CN' else work/'english-integration-v0.6'
        insert=zhroot/'insert' if args.language=='zh-CN' else enroot
        src=insert/'source';assets=src/'assets'
        for p in [assets,insert/'qa',insert/'output',integration/'qa',integration/'output',integration/'delivery',integration/'source',zhroot/'inputs',enroot/'inputs',zhroot/'evidence']:
            p.mkdir(parents=True,exist_ok=True)
        (zhroot/'inputs'/SPEC['inputs']['zh-CN']['filename']).symlink_to(zh)
        if en:(enroot/'inputs'/SPEC['inputs']['en']['filename']).symlink_to(en)
        for p in (SOURCE/args.language/'source').glob('*.py'):copy(p,src/p.name)
        for p in (SOURCE/'integration'/args.language).glob('*.py'):copy(p,integration/'source'/p.name)
        data_name='chart-data.json' if args.language=='zh-CN' else 'approved-zh-chart-data.json'
        text_name='content.json' if args.language=='zh-CN' else 'content-en.json'
        copy(SOURCE/'shared/chart-data.json',src/data_name)
        copy(SOURCE/args.language/'content.json',src/text_name)
        if args.language=='en':copy(SOURCE/'zh-CN/content.json',src/'approved-zh-content.json')
        shutil.copytree(SOURCE/'shared/evidence',insert/'evidence',dirs_exist_ok=True)
        copy(SOURCE/'shared/source-records.json',insert/'evidence/source-records.json')
        copy(SOURCE/'shared/evidence-ledger-en.json',insert/'evidence/evidence-ledger-en.json')
        copy(SOURCE/'shared/asset-world.svg',assets/'asset-world.svg')
        copy(SOURCE/'shared/logo-inputs.json',assets/'logos.json')
        logos=json.loads((assets/'logos.json').read_text())
        extracted=images_by_hash(zh,{row['sha256'] for row in logos})
        for row in logos:(assets/row['file']).write_bytes(extracted[row['sha256']])
        import fitz
        with fitz.open(assets/'asset-world.svg') as svg:
            with fitz.open('pdf',svg.convert_to_pdf()) as converted:converted.save(assets/'asset-world.pdf')
        if en:
            bg=SPEC['english_background']['sha256']
            (assets/'english-page-background.png').write_bytes(images_by_hash(en,{bg})[bg])
        run(src/'build_insert.py',env)
        tex='annual_change_insert' if args.language=='zh-CN' else 'annual_changes_en'
        command=['xelatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={insert/"output"}']
        if args.xelatex_fmt:command.append('-fmt='+str(Path(args.xelatex_fmt).resolve()))
        command.append(tex+'.tex')
        log=insert/'qa/compile.log'
        with log.open('w') as stream:
            for _ in range(2):subprocess.run(command,cwd=src,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True)
        if args.language=='zh-CN':
            run(src/'normalize_pdf_unicode.py',env)
            run(integration/'source/assemble.py',env)
            run(integration/'source/verify_integration.py',env)
            full=integration/'output/GOSD_2026_Essential_COSSI_zh-CN_v1.7.pdf'
            standalone=integration/'output/GOSD_2026_八大年度变化_中文两页_v0.5.pdf'
        else:
            run(src/'finalize_and_check.py',env)
            standalone=enroot/'delivery/GOSD_2026_COSSI_EN_Eight_Shifts_v0.1_Review.pdf'
            env['GOSD_REBUILT_INSERT_SHA256']=sha(standalone)
            run(integration/'source/integrate.py',env)
            run(integration/'source/verify.py',env)
            full=integration/'delivery/GOSD_2026_COSSI_EN_Full_Print_v0.6.pdf'
        output.mkdir(parents=True,exist_ok=True)
        for p in [full,standalone]:copy(p,output/p.name)
        for p in (integration/'qa').glob('*.json'):copy(p,output/'qa'/p.name)
        record={'language':args.language,'status':'source_reconstruction_verified','approved_artifact':SPEC['approved_full_artifacts'][args.language],
                'rebuilt':{'filename':full.name,'sha256':sha(full),'bytes':full.stat().st_size},
                'approved_pdf_bytes_identical':sha(full)==SPEC['approved_full_artifacts'][args.language]['sha256'],
                'source_data_sha256':sha(SOURCE/'shared/chart-data.json'),
                'note':'Validation compares page content, geometry, folios and navigation against the pinned input. Generated PDF serialization and source attachments may differ from the approved PDF.'}
        (output/'build-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as exc:
        print(f'Build failed: {exc}',file=sys.stderr)
        raise SystemExit(1)
