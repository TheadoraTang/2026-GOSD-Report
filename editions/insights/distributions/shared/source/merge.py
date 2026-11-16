"""Internal COSSI assembly stage called by the public build.py CLI.

Consumes the pinned Community PDF and generated five-page frontmatter in an
isolated work directory; the shared body is imported without reflow.
"""
from pathlib import Path
import argparse, hashlib, json, re, fitz
from fontTools.ttLib import TTFont
from fontTools import subset

parser=argparse.ArgumentParser()
parser.add_argument('--baseline',required=True)
parser.add_argument('--work-dir',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args()
ROOT=Path(args.work_dir).resolve()
SRC=ROOT/'source';OUT=ROOT/'output';QA=ROOT/'qa'
for d in [OUT,QA,SRC/'fonts']:d.mkdir(exist_ok=True,parents=True)
BASE=Path(args.baseline).resolve()
FRONT=ROOT/'frontmatter/output/frontmatter.pdf'
old=fitz.open(BASE);front=fitz.open(FRONT)
if len(old)!=140 or len(front)!=5:raise ValueError('Expected 140-page baseline and five frontmatter pages')
if hashlib.sha256(BASE.read_bytes()).hexdigest()!='ee89c8904dc1fc3e78e313e1f8dc17fcda6824db2d8daf8e206099610f272289':raise ValueError('Community baseline SHA256 mismatch')
def new_index(i):return i if i<4 else i+2
def roman(n):
    out=''
    for value,symbol in [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
        while n>=value:out+=symbol;n-=value
    return out

doc=fitz.open()
doc.insert_pdf(front,from_page=0,to_page=0,links=False)
doc.insert_pdf(old,from_page=1,to_page=1,links=False)
doc.insert_pdf(front,from_page=1,to_page=4,links=False)
doc.insert_pdf(old,from_page=4,to_page=139,links=False)
if len(doc)!=142:raise ValueError('Expected 142 assembled pages')

entries=[
 ('关于本报告・编委会','i—ii',2),
 ('开源创新专委会介绍','iii—iv',4),
 ('序言','v—vi',6),
 ('摘要・三种观察・行动','viii—x',9),
 ('研究框架・方法采用','xi—xii',12),
 ('标准化基础与在研进展','xiii—xiv',14),
 ('阅读路径・综合图指南','xv—xvi',16),
 ('宣言全文与结构','xvii—xix',18),
]
characters=''.join(t+p for t,p,_ in entries)+''.join(roman(n) for n in range(1,20))
fonts={}
for style in ['Regular','Bold']:
    path=SRC/'fonts'/f'NotoSansCJK-SC-{style}.otf'
    f=TTFont(ROOT/'font-inputs'/f'NotoSansCJK-{style}.ttc',fontNumber=2)
    options=subset.Options();options.retain_gids=True
    ss=subset.Subsetter(options=options);ss.populate(text=characters);ss.subset(f);f.save(path)
    fonts[style]=(path,fitz.Font(fontfile=str(path)))

# Remove only existing folio glyphs; keep the colored footer image and rules.
folio_changes=[]
for oi in range(4,19):
    ni=new_index(oi);page=doc[ni]
    spans=[s for b in page.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']
           if s['bbox'][0]>500 and s['bbox'][1]>798 and re.fullmatch(r'[ivxlcdm]+',s['text'])]
    if len(spans)!=1:raise ValueError(f'Unexpected folio structure on baseline page {oi+1}')
    s=spans[0];before=s['text'];after=roman(ni-1)
    page.add_redact_annot(fitz.Rect(s['bbox'])+(-.2,-.2,.2,.2),fill=False)
    page.apply_redactions(images=0,graphics=0,text=0)
    path,font=fonts['Bold'];page.insert_font(fontname='GOSDNewFolio',fontfile=str(path))
    size=s['size'];right=544.258
    page.insert_text((right-font.text_length(after,fontsize=size),s['origin'][1]),after,fontname='GOSDNewFolio',fontsize=size,color=(16/255,43/255,80/255))
    folio_changes.append(dict(old_physical=oi+1,new_physical=ni+1,before=before,after=after))

# Refit the frontmatter list to eight rows, preserving the chapter index and reading box.
contents=doc[8]
contents.add_redact_annot(fitz.Rect(49.5,219.5,383,374.5),fill=False)
contents.apply_redactions(images=0,graphics=0,text=0)
path,font=fonts['Regular'];contents.insert_font(fontname='GOSDNewTOC',fontfile=str(path))
toc_rects=[]
for row,(label,folio,target) in enumerate(entries):
    y=232.5+19.45*row;size=9.7634
    contents.insert_text((51.024,y),label,fontname='GOSDNewTOC',fontsize=size,color=(16/255,43/255,80/255))
    contents.insert_text((379.848-font.text_length(folio,fontsize=size),y),folio,fontname='GOSDNewTOC',fontsize=size,color=(89/255,110/255,130/255))
    toc_rects.append((fitz.Rect(50,y-12,382,y+4),target,label))

# Rebuild all original navigation explicitly so inserted/replaced page objects cannot leave stale destinations.
links=[]
def add_link(pi,l,origin):
    n={'kind':l['kind'],'from':fitz.Rect(l['from'])}
    if l['kind']==fitz.LINK_GOTO:
        n.update(page=l['page'],to=fitz.Point(l.get('to',(0,0))),zoom=l.get('zoom',0))
        if not 0<=n['page']<len(doc):raise ValueError('Internal link target outside document')
    elif l['kind']==fitz.LINK_URI:n['uri']=l['uri']
    else:raise ValueError(l)
    doc[pi].insert_link(n)
    links.append({'physical_page':pi+1,'kind':n['kind'],'rect':list(n['from']),'target_physical':n.get('page',-1)+1,'uri':n.get('uri'),'origin':origin})
for oi,pg in enumerate(old):
    for l in pg.get_links():
        if oi==6 and l['from'].x1<390 and 215<l['from'].y0<380:continue
        n=dict(l)
        if n['kind']==fitz.LINK_GOTO:n['page']=new_index(n['page'])
        add_link(new_index(oi),n,'v1.4 original, target remapped')
for rect,target,label in toc_rects:add_link(8,{'kind':1,'from':rect,'page':target},'Updated frontmatter contents: '+label)
for l in front[4].get_links():add_link(5,l,'Approved CCOSI contact')

toc=[]
for level,title,physical in old.get_toc():
    if title=='开放协作，共同未来' and physical==3:title='关于本报告'
    toc.append([level,title,new_index(physical-1)+1])
    if title=='编委会' and physical==4:
        toc.extend([[2,'中国科协联合国咨商开源创新专委会',5],[3,'开源创新与国际合作',6]])
doc.set_toc(toc)
doc.set_page_labels([
 {'startpage':0,'prefix':'Cover'}, {'startpage':1,'prefix':'Inside cover'},
 {'startpage':2,'style':'r','firstpagenum':1}, {'startpage':21,'prefix':'Blank'},
 {'startpage':22,'style':'D','firstpagenum':1},
 {'startpage':140,'prefix':'Inside back cover'}, {'startpage':141,'prefix':'Back cover'}])
doc.set_pagemode('UseOutlines')
doc.set_metadata(dict(title='2026 全球开源发展报告（精要版）- COSSI版 · v1.6页面重建',
 author='全球开源发展报告编写组；序言：王伟',subject='142页；获批前置页融入全文，目录、罗马页码、书签及内部跳转同步更新',
 keywords='GOSD,2026,精要版,全球开源发展报告,CCOSI,OSDGs,OSDI',creator='GOSD 2026 Report Assembly',producer='GOSD PDF-first workflow'))

# Preserve the historical approved baseline; attach a distinct reconstructed assembly record below.
for name in old.embfile_names():
    data=old.embfile_get(name)
    doc.embfile_add('Baseline_'+name,data,filename='Baseline_'+name,desc='Historical v1.4 baseline assembly source; superseded for current frontmatter and navigation by this reproducible COSSI build record')

manifest={'version':'COSSI zh-CN rebuilt from v1.6 approved pages','date':'2026-11-16','pages':142,'status':'reconstructed; page-faithful target is the approved v1.6 artifact, not byte-identical to that artifact',
 'baseline':{'file':BASE.name,'sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'pages':140},
 'frontmatter':{'file':FRONT.name,'sha256':hashlib.sha256(FRONT.read_bytes()).hexdigest(),'version':'v1.6 optical cover / approved frontmatter','pages':5},
 'authorization':'用户指定v1.6为COSSI版，并授权共享正文与双版本归档。',
 'cover_alignment':{'ccosi_width_pt':75,'singularity_width_pt':128.5,'ccosi_top_pt':773.1,'singularity_top_pt':772,'gap_pt':38,'order':['CCOSI','奇点智能研究院']},
 'modifications':['替换封面、关于本报告及编委会；编委会后新增两页CCOSI介绍与秘书长联系栏','统一前置罗马页码i—xix；正文印刷页码1—118保持','目录新增专委会介绍，所有书签和内部目标随物理页码更新','保留原79条外链，新增秘书长邮箱链接；源附件区分v1.4历史基线与本次COSSI可复现装配记录'],
 'confirmed_facts':['秘书处由中国通信学会承接','两位陈阳为不同人员，均保留','秘书长：王伟；华东师范大学数据学院；wwang@dase.ecnu.edu.cn'],
 'preserved':'除明确获批的前置页、目录与罗马页脚外，序言文字、其他前置内容、六章、附录、致谢和封底均保持；正文统计口径与事实未修改。',
 'folio_changes':folio_changes,'contents_entries':[{'label':a,'folio':b,'target_physical':c+1} for a,b,c in entries],
 'navigation':{'bookmarks':len(toc),'links':len(links),'internal_links':sum(l['kind']==1 for l in links),'external_links':sum(l['kind']==2 for l in links)},
 'pending':'本轮无新增事实待核；原模块既有事实和数据边界沿用，不因排版合并改变。','review_focus':['全书前置页与正文衔接','专委会介绍与联系栏','目录和书签导航']}
(SRC/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(SRC/'links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2))
(SRC/'bookmarks.json').write_text(json.dumps(toc,ensure_ascii=False,indent=2))
doc.embfile_add('COSSI_Rebuilt_Assembly_Record.json',json.dumps(manifest,ensure_ascii=False,indent=2).encode(),filename='COSSI_Rebuilt_Assembly_Record.json',desc='Reconstructed assembly record; approved artifact and rebuilt output are distinct')
target=Path(args.output).resolve();doc.save(target,garbage=4,deflate=True)
print(json.dumps({'file':str(target),'pages':len(doc),'bytes':target.stat().st_size,**manifest['navigation']},ensure_ascii=False))
