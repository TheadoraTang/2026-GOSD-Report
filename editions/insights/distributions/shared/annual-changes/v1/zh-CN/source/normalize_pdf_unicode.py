"""Restore source punctuation in shared-glyph CJK ToUnicode mappings.

Noto CJK may map shared glyphs to a compatibility character. This changes
only extraction mappings, never the rendered page or embedded font.
"""
from pathlib import Path
import fitz,re,json
R=Path(__file__).resolve().parents[1]
p=R/'output/annual_change_insert.pdf';d=fitz.open(p)
refs=set()
for pg in d:
    for f in pg.get_fonts():
        typ,val=d.xref_get_key(f[0],'ToUnicode')
        if typ=='xref':refs.add(int(val.split()[0]))
changes=[]
for xref in refs:
    s=d.xref_stream(xref);old=s
    for src,dst in [(b'2011',b'002D'),(b'30FB',b'00B7')]:
        s,n=re.subn(rb'(<[0-9A-Fa-f]+>\s*)<'+src+rb'>',lambda m:m.group(1)+b'<'+dst+b'>',s)
        if n:changes.append({'xref':xref,'from':src.decode(),'to':dst.decode(),'count':n})
    if s!=old:d.update_stream(xref,s)
tmp=p.with_suffix('.normalized.pdf');d.save(tmp,garbage=4,deflate=True);d.close();tmp.replace(p)
(R/'qa/unicode.json').write_text(json.dumps(changes,indent=2))
print('Normalized extraction mappings:',len(changes))
