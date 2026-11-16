"""Build pinned Community or COSSI distributions without storing binary inputs in Git."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

SOURCE = Path(__file__).resolve().parent


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def require_file(path, spec):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError(f"Missing input: {spec['name'] if 'name' in spec else spec['filename']}")
    actual = digest(path)
    if actual != spec['sha256']:
        raise ValueError(f"Input SHA256 mismatch for {path.name}: expected {spec['sha256']}, got {actual}")
    return path


def find_font(spec, assets):
    supplied = assets / 'fonts' / spec['name']
    if supplied.is_file():
        return require_file(supplied, spec)
    try:
        result = subprocess.run(
            ['fc-match', '-f', '%{file}\n%{index}\n', f"{spec['family']}:style={spec['style']}"],
            check=True, text=True, capture_output=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"Provide pinned font at assets-dir/fonts/{spec['name']}; fontconfig discovery failed") from exc
    if len(result) < 2 or int(result[1]) != spec['collection_index']:
        raise ValueError(f"Font collection index mismatch for {spec['name']}; expected SC index {spec['collection_index']}")
    return require_file(result[0], spec)


def run(script, *args):
    subprocess.run([sys.executable, str(SOURCE / script), *map(str, args)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--distribution', required=True, choices=['cossi', 'community'])
    parser.add_argument('--language', required=True, choices=['zh-CN', 'en'])
    parser.add_argument('--community-baseline')
    parser.add_argument('--output')
    parser.add_argument('--assets-dir')
    args = parser.parse_args()
    # Do not create directories or artifacts for a planned language.
    if args.language == 'en':
        parser.error('English is planned; no approved English text, layout, or artifact exists. Build refused.')
    if not args.community_baseline or not args.output:
        parser.error('--community-baseline and --output are required for an available build')
    specs = json.loads((SOURCE / 'input-materials.json').read_text())
    baseline = require_file(args.community_baseline, specs['community_baseline'])
    output = Path(args.output).resolve()
    if baseline == output:
        raise ValueError('Choose a distinct output; the pinned baseline is read-only')
    repository = next((p for p in SOURCE.parents if (p / '.git').exists()), None)
    if repository and (output == repository or repository in output.parents):
        raise ValueError('PDF outputs must be outside the Git repository')
    asset_paths = {}
    font_paths = {}
    if args.distribution == 'cossi':
        if not args.assets_dir:
            parser.error('COSSI requires --assets-dir with the five inputs pinned in input-materials.json')
        assets = Path(args.assets_dir).resolve()
        asset_paths = {s['name']: require_file(assets / s['name'], s) for s in specs['external_assets']}
        font_paths = {s['name']: find_font(s, assets) for s in specs['external_fonts']}
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.distribution == 'community':
        shutil.copyfile(baseline, output)
    else:
        with tempfile.TemporaryDirectory(prefix='gosd-cossi-build-') as temporary:
            work = Path(temporary)
            front = work / 'frontmatter'
            for folder in [work / 'source', work / 'font-inputs', front / 'source' / 'assets', front / 'font-inputs', front / 'content']:
                folder.mkdir(parents=True, exist_ok=True)
            for name, path in asset_paths.items():
                (front / 'source' / 'assets' / name).symlink_to(path)
            for name, path in font_paths.items():
                (front / 'font-inputs' / name).symlink_to(path)
                (work / 'font-inputs' / name).symlink_to(path)
            for path in (SOURCE / 'content').glob('*.json'):
                shutil.copyfile(path, front / 'content' / path.name)
            shutil.copyfile(SOURCE / 'diagrams' / 'ccosi-work-system.json', front / 'source' / 'assets' / 'ccosi-work-system.json')
            run('frontmatter/build_layout.py', '--work-dir', front)
            run('frontmatter/render.py', '--work-dir', front)
            run('merge.py', '--baseline', baseline, '--work-dir', work, '--output', output)
    record = {
        'distribution': args.distribution,
        'language': args.language,
        'artifact_status': 'approved_artifact_exact_copy' if args.distribution == 'community' else 'reconstructed_from_approved_page_sources',
        'approved_artifact': specs['approved_artifacts'][args.distribution],
        'output': {'filename': output.name, 'sha256': digest(output), 'size_bytes': output.stat().st_size},
        'baseline_sha256': specs['community_baseline']['sha256'],
        'external_assets_verified': list(asset_paths),
        'font_inputs_verified': list(font_paths),
        'note': 'COSSI reconstruction targets approved v1.6 page content and layout; PDF bytes and embedded attachment set are not claimed identical.',
    }
    output.with_suffix('.build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'Build failed: {exc}', file=sys.stderr)
        raise SystemExit(1)
