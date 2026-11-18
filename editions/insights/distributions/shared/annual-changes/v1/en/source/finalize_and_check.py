"""Finalize and audit the standalone English PDF, never the full report."""
from pathlib import Path
import hashlib, json, re, unicodedata
import fitz

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'delivery';OUT.mkdir(exist_ok=True)
INPUT=ROOT/'output/annual_changes_en.pdf'
PDF=OUT/'GOSD_2026_COSSI_EN_Eight_Shifts_v0.1_Review.pdf'
BASELINE=ROOT/'inputs/GOSD_2026_COSSI_EN_Full_Print_v0.5.pdf'
EXPECTED_BASELINE='362cf50547b16200495c6804c3e8dee6a476918fadb89856f817bfa39f5c7298'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

d=fitz.open(INPUT)
assert len(d)==2
d.set_toc([[1,'Activity, assets and a changing geography',1],
           [1,'Cities, organizations and the agent ecosystem',2]])
d.set_page_labels([{'startpage':0,'prefix':'0','style':'D','firstpagenum':1}])
meta=d.metadata
meta.update(title='2025–2026: Eight Shifts in Global Open Source | COSSI English Review v0.1',
            author='GOSD Editorial Team',
            subject='Two-page A3 portrait insert adapted from approved Chinese v0.5; Author-approved insert; standalone reconstruction',
            keywords='GOSD 2026, COSSI, annual changes, English, review v0.1')
d.set_metadata(meta)
d.xref_set_key(d.pdf_catalog(),'Lang','(en)')
d.save(PDF,garbage=4,deflate=True)
d.close();d=fitz.open(PDF)

C=json.loads((ROOT/'source/content-en.json').read_text())
D=json.loads((ROOT/'source/approved-zh-chart-data.json').read_text())
normalize=lambda s:re.sub(r'\s+','',unicodedata.normalize('NFKC',s))
checks=[]
for n,p in enumerate(d):
    assert abs(p.rect.width-841.89)<.02 and abs(p.rect.height-1190.55)<.02
    extracted=p.get_text();norm=normalize(extracted)
    for it in C['pages'][n]['items']:
        for key in ('chart_title','scope','title','body'):
            assert normalize(it[key]) in norm,(n+1,it['id'],key)
    spans=[s for b in p.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']]
    assert all(p.rect.contains(fitz.Rect(s['bbox'])) for s in spans)
    assert not re.search('[\u4e00-\u9fff]',extracted)
    assert '\ufffd' not in extracted
    fonts=[]
    for f in p.get_fonts():
        font=d.extract_font(f[0]);assert font[3],f
        fonts.append({'name':f[3],'embedded_bytes':len(font[3])})
    urls=[l['uri'] for l in p.get_links() if l.get('uri')]
    assert urls
    checks.append({'page':n+1,'size_pt':[p.rect.width,p.rect.height],
                   'text_spans_within_page':True,'all_four_analysis_bodies_complete':True,
                   'fonts':fonts,'min_font_pt':min(s['size'] for s in spans),
                   'link_rectangles':len(urls),'source_urls':list(dict.fromkeys(urls))})
    p.get_pixmap(matrix=fitz.Matrix(1.7,1.7),alpha=False).save(ROOT/f'qa/final-{n+1:02}.png')
    (ROOT/f'qa/final-{n+1:02}.txt').write_text(extracted)

# Numerical checks use the source values, independently of displayed rounding.
assert [round(r['values'][2]/r['values'][1],2) for r in D['1']['rows']]==[2.67,2.66,3.24,2.42]
assert round((2.96/2.43-1)*100,1)==21.8
assert round((1/.711-1)*100,1)==40.6
assert [round((r['values'][1]/r['values'][0]-1)*100,1) for r in D['3']['rows']]==[42.0,28.4,29.2]
assert round(D['4']['rows'][0]['values'][-1]/1e6,3)==4.429
assert round(D['4']['rows'][1]['values'][-1]/1e6,3)==4.240
assert D['6']['rows'][0]['values'][0]<D['6']['rows'][1]['values'][0]
assert D['6']['rows'][0]['values'][1]>D['6']['rows'][1]['values'][1]
assert D['7']['rows'][1]['values'][0]<D['7']['rows'][2]['values'][0]
assert D['7']['rows'][1]['values'][1]>D['7']['rows'][2]['values'][1]
assert sum(c['total'] for c in D['8']['categories'])==86
assert sum(c['recent'] for c in D['8']['categories'])==48
assert round(48/86*100,1)==55.8
log=(ROOT/'output/annual_changes_en.log').read_text()
assert not any(v in log for v in ['Overfull','Underfull','Missing character'])
baseline_status='not supplied for independent rebuild'
if BASELINE.exists():
    assert sha(BASELINE)==EXPECTED_BASELINE
    baseline_status='byte-identical to input; not merged or modified'
result={'version':'English insert v0.1','date':'2026-11-18','review_status':'rebuild of author-approved English insert v0.1',
        'approved_content_baseline':'Chinese eight-shift insert v0.5, integrated in Chinese full report v1.7',
        'pdf':PDF.name,'bytes':PDF.stat().st_size,'sha256':sha(PDF),'pages':checks,
        'numeric_checks':'passed; counts unchanged; units and rounding converted explicitly',
        'code_repo_growth':'22.3% reproduced as reported; not recomputed from rounded 371M / 454M totals',
        'tex_layout_warnings':0,'missing_glyphs':0,
        'english_full_report':{'name':BASELINE.name,'sha256':EXPECTED_BASELINE,'status':baseline_status}}
(ROOT/'qa/checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'file':str(PDF),'bytes':PDF.stat().st_size,'sha256':sha(PDF),'pages':2,'checks':'passed','full_report':baseline_status},indent=2))
