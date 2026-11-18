"""Integrate the approved English two-page insert into print report v0.6.

The input PDFs are immutable. Existing PDF pages are preserved as vectors;
only the contents, two narrative transitions and front-matter folios change.
"""
from pathlib import Path
from io import BytesIO
import json, hashlib, os
import fitz
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

R=Path(__file__).resolve().parents[1]
BASE=R.parent/'year-change-en-v0.1/inputs/GOSD_2026_COSSI_EN_Full_Print_v0.5.pdf'
INSERT=R.parent/'year-change-en-v0.1/delivery/GOSD_2026_COSSI_EN_Eight_Shifts_v0.1_Review.pdf'
OUTPUT=R/'delivery/GOSD_2026_COSSI_EN_Full_Print_v0.6.pdf'
BASE_SHA='362cf50547b16200495c6804c3e8dee6a476918fadb89856f817bfa39f5c7298'
INSERT_SHA=os.environ.get('GOSD_REBUILT_INSERT_SHA256','a44ddb30f4b0caa337c8d83c082d72c0d0ab3aa6f4333ff08e6faa1da10672c9')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE)==BASE_SHA
assert sha(INSERT)==INSERT_SHA
for f in ['qa','delivery']:(R/f).mkdir(exist_ok=True)

REG='/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'
BOLD='/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('GOSDReg',REG))
pdfmetrics.registerFont(TTFont('GOSDBold',BOLD))
NAVY=(.067,.173,.325)
BODY=(.141,.212,.298)
MUTED=(.349,.431,.510)
TEAL=(0,.494,.525)
WIDTH,HEIGHT=841.88977,1190.55115
edits=[]

def roman(n):
    out=''
    for v,c in [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
        while n>=v:out+=c;n-=v
    return out

def overlay(page, draw):
    bio=BytesIO();c=canvas.Canvas(bio,pagesize=(WIDTH,HEIGHT),pageCompression=1)
    draw(c);c.showPage();c.save()
    with fitz.open(stream=bio.getvalue(),filetype='pdf') as stamp:
        page.show_pdf_page(page.rect,stamp,0)

def string(c,x,baseline,s,size=13,bold=False,color=BODY):
    c.setFont('GOSDBold' if bold else 'GOSDReg',size)
    c.setFillColorRGB(*color);c.drawString(x,HEIGHT-baseline,s)

def para(c,x,baseline,w,s,size,leading,bold=False,color=BODY):
    rows=simpleSplit(s,'GOSDBold' if bold else 'GOSDReg',size,w)
    for i,row in enumerate(rows):string(c,x,baseline+i*leading,row,size,bold,color)
    return len(rows)

def erase_text(page,rect):
    page.add_redact_annot(rect,fill=(1,1,1))
    # Retain images and vector graphics; remove only the selected text.
    page.apply_redactions(images=0,graphics=0,text=0)

def set_folio(page,label):
    erase_text(page,fitz.Rect(742,1157,798,1178))
    def draw(c):
        c.setFont('GOSDBold',10);c.setFillColorRGB(*MUTED)
        c.drawRightString(791.88977,HEIGHT-1171,label)
    overlay(page,draw)

doc=fitz.open(BASE)
original_toc=doc.get_toc(False)
insert=fitz.open(INSERT)
doc.insert_pdf(insert,start_at=13)
assert len(doc)==158

# Existing destinations refer to page objects; insertion preserves these links.
# Front matter occupies physical pages 2–28 (folios i–xxvii).
for index in range(13,28):set_folio(doc[index],roman(index))
edits.append({'kind':'folios','physical_pages':'14–28','new_folios':'xiii–xxvii'})

# Rebuild only the front-matter column, preserving the approved right column.
page=doc[9]
for link in page.get_links():
    r=link['from']
    if r.x0<410 and r.y0>340 and r.y0<1000:page.delete_link(link)
erase_text(page,fitz.Rect(45,344,414,960))
front=[
 ('About this report','i',1),('Editorial Board','ii',2),('About CCOSI','iii',3),
 ('Preface','vi',6),('Contents','ix',9),('Executive summary','x',10),
 ('Three views, three distributions','xi',11),('From evidence to action','xii',12),
 ('Eight shifts in global open source','xiii–xiv',13),
 ('A shared language for observation','xv',15),('Putting the framework to use','xvi',16),
 ('Standardization foundations and standards in development','xvii',17),
 ('Report architecture and reading routes','xx',20),('How to read a composite figure','xxii',22),
 ('Declaration on international cooperation in open source AI','xxiii',23)]
front_links=[]
def draw_front(c):
    baseline=365
    for title,label,target in front:
        new=(target==13)
        rows=para(c,50,baseline,286,title,13,18,new,TEAL if new else BODY)
        c.setFont('GOSDBold',12);c.setFillColorRGB(*TEAL)
        c.drawRightString(395,HEIGHT-baseline,label)
        front_links.append({'title':title,'folio':label,'target_index':target,
                            'rect':[50,baseline-14,405,baseline+12+(rows-1)*18]})
        baseline+=36 if rows==1 else 53
overlay(page,draw_front)
for row in front_links:
    page.insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(row['rect']),'page':row['target_index'],'to':fitz.Point(0,0)})

# The reading route includes the newly integrated section.
# Its pale background must be restored after text redaction.
erase_text(page,fitz.Rect(58,235,285,270))
def draw_route(c):
    c.setFillColorRGB(.945098,.964706,.972549)
    c.rect(56,HEIGHT-272,231,39,fill=1,stroke=0)
    para(c,61,249.5,222,'Executive summary and annual shifts, then Chapter 6',10.5,15,False,MUTED)
overlay(page,draw_route)
page.insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(50,203,289.2966003417969,273),'page':10,'to':fitz.Point(0,0)})

erase_text(page,fitz.Rect(46,1080,791,1122))
note='Front matter uses Roman numerals. Chapters and the appendix share continuous page numbering. Detailed section guides appear on pages xx–xxi.'
overlay(page,lambda c:para(c,50,1096.5,741.89,note,11.5,17,False,MUTED))
edits.append({'kind':'contents','physical_page':10,'entries':front_links,
              'reading_route':'Executive summary and annual shifts, then Chapter 6',
              'section_guide_reference':'xx–xxi'})

# A short bridge connects the executive summary to the insert.
bridge='The following eight shifts put these priorities in context, connecting changes in activity and assets with the roles of regions, cities and institutions.'
def draw_bridge(c):
    c.setStrokeColorRGB(.812,.863,.898);c.setLineWidth(.55)
    c.line(66.5074,HEIGHT-1024,774.9915,HEIGHT-1024)
    para(c,66.5074,1048,708.4841,bridge,12.4,17.5,False,MUTED)
overlay(doc[12],draw_bridge)
edits.append({'kind':'transition-before','physical_page':13,'text':bridge})

# Adapt the following framework lead in the same three-line text area.
following='Interpreting these shifts requires shared goals and comparable evidence. OSDGs set the development direction; OSDI translates goals into observable dimensions. The assessment data schema records objects, periods, sources and versions so findings can be explained and verified.'
erase_text(doc[15],fitz.Rect(63,228,778,298))
overlay(doc[15],lambda c:para(c,66.5074,246.7683,708.4841,following,14.84847,21.2121,False,BODY))
edits.append({'kind':'transition-after','physical_page':16,'text':following})

# Update bookmarks while preserving titles, nesting and destination positions.
toc=[]
for level,title,target,detail in original_toc:
    newtarget=target+(2 if target>=14 else 0)
    dest={k:v for k,v in detail.items() if k in ('kind','to','zoom','color','bold','italic','collapse')}
    dest['page']=newtarget-1
    toc.append([level,title,newtarget,dest])
    if title=='From evidence to action':
        toc.extend([[1,'2025–2026: Eight shifts in global open source',14],
                    [2,'Activity, assets and a changing geography',14],
                    [2,'Cities, organizations and the agent ecosystem',15]])
doc.set_toc(toc)
doc.set_page_labels([
 {'startpage':0,'prefix':'Cover','firstpagenum':1},
 {'startpage':1,'prefix':'','firstpagenum':1,'style':'r'},
 {'startpage':28,'prefix':'','firstpagenum':1,'style':'D'},
 {'startpage':157,'prefix':'Back cover','firstpagenum':1}])

# Link the insert's section references to the relevant body sections.
simple_toc=doc.get_toc()
def section(number):
    candidates=[p-1 for level,title,p in simple_toc if level==2 and title.startswith(number+' ')]
    assert candidates,(number,'missing destination')
    return candidates[0]
internal_added=[]
for pidx,token,target in [(13,'§2.5',section('2.5')),
                           (13,'§§2.1–2.2',section('2.1')),
                           (14,'§§3.2–3.3',section('3.2')),
                           (14,'§4.1',section('4.1'))]:
    for r in doc[pidx].search_for(token):
        doc[pidx].insert_link({'kind':fitz.LINK_GOTO,'from':r,'page':target,'to':fitz.Point(0,0)})
        internal_added.append({'physical_page':pidx+1,'token':token,'target_page':target+1})

meta=doc.metadata
meta.update(title='2026 Global Open Source Development Report | COSSI English Edition | Print v0.6',
 author='GOSD editorial team',
 subject='Complete essential edition, A3 portrait, 158 reader-order pages; integrated eight annual shifts; long-edge duplex; Roman front matter and continuous body folios',
 keywords='GOSD 2026, COSSI, English, essential edition, print v0.6, eight annual shifts',
 modDate='D:20261118000000+08\'00\'')
doc.set_metadata(meta)
doc.xref_set_key(doc.pdf_catalog(),'Lang','(en)')
# Retain the existing print-viewer preferences from the approved baseline.
doc.save(OUTPUT,garbage=4,deflate=True)
doc.close();insert.close()
record={'version':'0.6','date':'2026-11-18','status':'approved English insert integrated',
        'base':{'name':BASE.name,'sha256':BASE_SHA,'pages':156},
        'insert':{'name':INSERT.name,'sha256':INSERT_SHA,'pages':2,'approved_by':'user, 2026-11-18'},
        'output':{'name':OUTPUT.name,'sha256':sha(OUTPUT),'bytes':OUTPUT.stat().st_size,'pages':158},
        'insert_position':{'physical_pages':[14,15],'folios':['xiii','xiv']},
        'body_folios':'1–129 unchanged','front_folios':'i–xxvii',
        'bookmarks':len(toc),'internal_references_added':internal_added,'edits':edits}
(R/'qa/integration-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['version','output','insert_position','bookmarks']},indent=2))
