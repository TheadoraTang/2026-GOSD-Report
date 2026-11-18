"""Check page preservation, numbering, destinations, text and print geometry."""
from pathlib import Path
import fitz, json, re, hashlib
import numpy as np

R=Path(__file__).resolve().parents[1]
B=R.parent/'year-change-en-v0.1/inputs/GOSD_2026_COSSI_EN_Full_Print_v0.5.pdf'
I=R.parent/'year-change-en-v0.1/delivery/GOSD_2026_COSSI_EN_Eight_Shifts_v0.1_Review.pdf'
P=R/'delivery/GOSD_2026_COSSI_EN_Full_Print_v0.6.pdf'
b=fitz.open(B);ins=fitz.open(I);f=fitz.open(P)
record=json.loads((R/'qa/integration-record.json').read_text())
assert len(b)==156 and len(f)==158 and len(ins)==2
assert all(abs(p.rect.width-841.89)<.02 and abs(p.rect.height-1190.55)<.02 for p in f)
map_index=lambda i:i+2 if i>=13 else i
normalize=lambda s:re.sub(r'\s+','',s)

def roman(n):
    out=''
    for v,c in [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
        while n>=v:out+=c;n-=v
    return out

# Continuous logical and printed folios; unchanged body pagination.
for index in range(1,28):
    assert f[index].get_label()==roman(index)
    assert f[index].get_text(clip=fitz.Rect(740,1155,811,1180)).strip()==roman(index)
blank_body_folios=[]
for index in range(28,157):
    assert f[index].get_label()==str(index-27)
    printed=f[index].get_text(clip=fitz.Rect(740,1155,811,1180)).strip()
    if not b[index-2].get_text().strip():
        assert not f[index].get_text().strip()
        blank_body_folios.append(index-27)
    else:
        assert printed==str(index-27),(index+1,printed)
assert blank_body_folios==[18,40,108]
assert f[0].get_label()=='Cover' and f[157].get_label()=='Back cover'

# Preserve all 129 body/appendix/acknowledgment pages, plus the back cover.
for old in range(26,156):
    assert normalize(b[old].get_text())==normalize(f[old+2].get_text()),('body text changed',old+1)

# Retain old internal and external links except the deliberately rebuilt
# front-matter contents rows. Their new links are checked separately.
link_count=0
for old,p in enumerate(b):
    for link in p.get_links():
        if old==9 and link['from'].x0<410 and 340<link['from'].y0<1000:continue
        candidates=[l for l in f[map_index(old)].get_links()
                    if l['kind']==link['kind'] and l['from']==link['from']]
        if link['kind']==fitz.LINK_GOTO:
            assert any(l['page']==map_index(link['page']) and l.get('to')==link.get('to') for l in candidates),(old,link)
        elif link.get('uri'):
            assert any(l.get('uri')==link['uri'] for l in candidates),(old,link)
        link_count+=1
for edit in record['edits']:
    if edit['kind']=='contents':
        for row in edit['entries']:
            assert any(l['kind']==fitz.LINK_GOTO and l['page']==row['target_index']
                       and l['from']==fitz.Rect(row['rect']) for l in f[9].get_links()),row
for p in f:
    for l in p.get_links():
        if l['kind']==fitz.LINK_GOTO:assert 0<=l['page']<len(f)

toc=f.get_toc()
assert len(toc)==118
for level,title,pno in b.get_toc():
    expected=pno+2 if pno>=14 else pno
    assert [level,title,expected] in toc,(title,expected)
assert [1,'2025–2026: Eight shifts in global open source',14] in toc
assert 'pages xx–xxi.' in f[9].get_text()
assert 'pages xviii–xix.' not in f[9].get_text()

# Compare every original page visually outside explicitly edited rectangles.
# A small mask expansion excludes antialiasing at the edit boundary.
scale=.70
visual=[]
def rgb(page):
    p=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
    return np.frombuffer(p.samples,dtype=np.uint8).reshape(p.height,p.width,3)
for old,p in enumerate(b):
    a=rgb(p);z=rgb(f[map_index(old)]);assert a.shape==z.shape
    mask=np.zeros(a.shape[:2],dtype=bool)
    regions=[]
    if 13<=old<=25:regions.append((738,1153,803,1182))
    if old==9:regions += [(42,341,417,964),(55,232,288,274),(43,1077,794,1126)]
    if old==12:regions.append((63,1020,779,1079))
    if old==13:regions.append((60,225,782,302))
    for x0,y0,x1,y1 in regions:
        mask[max(0,int(y0*scale)):min(mask.shape[0],int(y1*scale)+2),
             max(0,int(x0*scale)):min(mask.shape[1],int(x1*scale)+2)]=True
    diff=np.any(a!=z,axis=2)&~mask
    count=int(diff.sum())
    visual.append({'original_page':old+1,'final_page':map_index(old)+1,'changed_pixels_outside_edits':count})
    assert count==0,('unexpected visual change',old+1,count)

# Redaction serialization can change antialiasing at a few curve-edge pixels.
# Check text equality and tightly bound that observed rounding difference.
insert_visual=[]
for j in range(2):
    a=rgb(ins[j]);z=rgb(f[13+j]);limit=int(1145*scale)
    delta=np.max(np.abs(a[:limit].astype(int)-z[:limit].astype(int)),axis=2)
    changed=int((delta>0).sum());maximum=int(delta.max())
    assert maximum<=8 and changed<=30,('insert altered',j+1,changed,maximum)
    clip=fitz.Rect(0,0,842,1145)
    assert ins[j].get_text(clip=clip)==f[13+j].get_text(clip=clip)
    insert_visual.append({'page':j+1,'antialias_pixels':changed,'maximum_channel_delta':maximum,'text_unchanged':True})

# Fonts actually used by PDF text spans must remain embedded.
font_records={};used=set()
for p in f:
    for bl in p.get_text('dict')['blocks']:
        for line in bl.get('lines',[]):
            for s in line['spans']:used.add(s['font'])
    for resource in p.get_fonts():font_records[resource[0]]=resource
unembedded=[]
for xref,resource in font_records.items():
    short=resource[3].split('+')[-1]
    if short in used:
        ff=f.extract_font(xref)
        if not ff[3]:unembedded.append({'font':short,'xref':xref})
assert not unembedded,unembedded

# Render edited pages and the chapter/back-cover boundaries for final viewing.
for i in [9,12,13,14,15,27,28,156,157]:
    f[i].get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(R/f'qa/final-{i+1:03}.png')
result={'version':'0.6','date':'2026-11-18','pages':158,'size':'A3 portrait, 297 × 420 mm',
        'front_matter_folios':'i–xxvii','body_folios':'1–129','body_start_physical_page':29,'retained_blank_duplex_folios':blank_body_folios,
        'insert_physical_pages':[14,15],'insert_folios':['xiii','xiv'],
        'bookmarks':118,'total_links':sum(len(p.get_links()) for p in f),
        'preserved_original_links_checked':link_count,
        'body_text_checks':'130 pages unchanged, including back cover',
        'visual_comparison':'156 original pages pixel-identical outside declared edit areas',
        'insert_visual_comparison':insert_visual,
        'unembedded_used_fonts':unembedded,'inputs_unchanged':True,
        'pdf_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),
        'visual_details':visual}
assert hashlib.sha256(B.read_bytes()).hexdigest()==record['base']['sha256']
assert hashlib.sha256(I.read_bytes()).hexdigest()==record['insert']['sha256']
(R/'qa/verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='visual_details'},ensure_ascii=False,indent=2))
