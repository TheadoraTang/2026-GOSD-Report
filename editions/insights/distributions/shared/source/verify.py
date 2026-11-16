"""Compare a rebuilt PDF with the pinned approved artifact, page by page."""
from pathlib import Path
import argparse
import hashlib
import json
import fitz


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalized_links(doc):
    records = []
    for page in doc:
        items = []
        for link in page.get_links():
            item = {k: (list(v) if isinstance(v, (fitz.Rect, fitz.Point)) else v)
                    for k, v in link.items() if k not in ['id', 'xref']}
            items.append(item)
        records.append(sorted(items, key=lambda x: json.dumps(x, sort_keys=True)))
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--distribution', required=True, choices=['cossi', 'community'])
    parser.add_argument('--rebuilt', required=True)
    parser.add_argument('--approved', required=True)
    parser.add_argument('--qa', required=True)
    parser.add_argument('--dpi', type=int, default=72)
    args = parser.parse_args()
    specs = json.loads((Path(__file__).resolve().parent / 'input-materials.json').read_text())
    expected = specs['approved_artifacts'][args.distribution]
    if sha(args.approved) != expected['sha256']:
        parser.error('Approved reference SHA256 does not match the registered artifact')
    if args.dpi < 36:
        parser.error('Use at least 36 dpi for the page comparison')
    approved, rebuilt = fitz.open(args.approved), fitz.open(args.rebuilt)
    rows = []
    for i in range(min(len(approved), len(rebuilt))):
        a, b = approved[i], rebuilt[i]
        pa = a.get_pixmap(matrix=fitz.Matrix(args.dpi / 72, args.dpi / 72))
        pb = b.get_pixmap(matrix=fitz.Matrix(args.dpi / 72, args.dpi / 72))
        rows.append({'physical_page': i + 1, 'text_identical': a.get_text() == b.get_text(),
                     'pixels_identical': (pa.width, pa.height, pa.samples) == (pb.width, pb.height, pb.samples),
                     'approved_pixels_sha256': hashlib.sha256(pa.samples).hexdigest(),
                     'rebuilt_pixels_sha256': hashlib.sha256(pb.samples).hexdigest()})
    report = {'distribution': args.distribution, 'approved_sha256': expected['sha256'],
              'rebuilt_sha256': sha(args.rebuilt), 'dpi': args.dpi,
              'page_count_expected': expected['pages'], 'page_count_actual': len(rebuilt),
              'all_page_text_identical': all(r['text_identical'] for r in rows),
              'all_page_pixels_identical': all(r['pixels_identical'] for r in rows),
              'bookmarks_identical': approved.get_toc() == rebuilt.get_toc(),
              'page_labels_identical': approved.get_page_labels() == rebuilt.get_page_labels(),
              'links_identical': normalized_links(approved) == normalized_links(rebuilt),
              'artifact_byte_identical': sha(args.approved) == sha(args.rebuilt),
              'approved_attachments': approved.embfile_names(), 'rebuilt_attachments': rebuilt.embfile_names(),
              'attachment_scope': ('Community is an exact copy of the approved v1.4 PDF, including its historical attachments.' if args.distribution == 'community' else 'Rebuilt COSSI preserves the historical baseline source and includes its new assembly record; it does not impersonate the approved artifact attachment bundle.'),
              'pages': rows}
    report['passed'] = (len(approved) == len(rebuilt) == expected['pages'] and
                        all(report[k] for k in ['all_page_text_identical', 'all_page_pixels_identical',
                                                'bookmarks_identical', 'page_labels_identical', 'links_identical']) and
                        (args.distribution != 'community' or report['artifact_byte_identical']))
    qa = Path(args.qa).resolve()
    qa.parent.mkdir(parents=True, exist_ok=True)
    qa.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'pages'}, ensure_ascii=False, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
