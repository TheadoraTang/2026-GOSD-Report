"""Assemble the approved COSSI Chinese report and the polished annual-change insert.

All original PDF pages are imported without reflow. Only the contents, the
framework transition, frontmatter folios and the appendix reading guide change.
Printed p.116 (previously blank) becomes the evidence index for the insert.
"""
from pathlib import Path
import json, hashlib, re, copy, zipfile
import fitz
from fontTools.ttLib import TTFont
from fontTools import subset

R=Path(__file__).resolve().parents[1]
BASE=R/'inputs/GOSD_2026_Essential_COSSI_zh-CN_v1.6.pdf'
ART=R/'insert/output/annual_change_insert.pdf'
OUT=R/'output'; QA=R/'qa'; SRC=R/'source'
for folder in [OUT,QA,SRC/'fonts']: folder.mkdir(parents=True,exist_ok=True)
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='d43329e97954c8e2eba2392ba5ad437d5c4c8dcb37bd7ba2ede9be5e190ae5b0'
old=fitz.open(BASE); art=fitz.open(ART)
assert len(old)==142 and len(art)==2
MM=72/25.4; NAVY=(16/255,43/255,80/255); MUTED=(89/255,110/255,130/255); TEAL=(0,.498,.522)
BRIDGE='上述变化涉及不同对象与指标，需要共同的观察语言。OSDGs明确发展方向，OSDI将目标转化为可观察维度；评价数据结构保留对象、期间、来源与版本，支持解释和复核。'
ENTRIES=[
 ('关于本报告・编委会','i—ii',2),
 ('开源创新专委会介绍','iii—iv',4),
 ('序言','v—vi',6),
 ('摘要・三种观察・行动','viii—x',9),
 ('2025—2026：全球开源的八大变化','xi—xii',12),
 ('研究框架・方法采用','xiii—xiv',14),
 ('标准化基础与在研进展','xv—xvi',16),
 ('阅读路径・综合图指南','xvii—xviii',18),
 ('宣言全文与结构','xix—xxi',20),
]
EVIDENCE=[
 {'id':1,'title':'开发活动与智能体使用','source':'GitHub Octoverse 2026；截至各年9月30日的12个月，含公开与私有仓库。','boundary':'四组活动分别比较；AI起草PR占比另按2026年3月、9月观察。增长不等于因果贡献。','url':'https://github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents/'},
 {'id':2,'title':'代码、模型与数据资产','source':'本报告第27页／图2-13；Hugging Face《State of Open Models: Summer 2026》。','boundary':'代码为2025Q2—2026Q2；HF为2026年1—8月，含期后。模型与数据增幅由约数计算。','url':'https://huggingface.co/blog/state-of-open-models-summer-2026','printed':27},
 {'id':3,'title':'全球南方参与增长','source':'本报告第16页及2.1地区比较表；2025、2026报告年度的活跃开发者序列。','boundary':'六国为巴西、印尼、越南、埃及、菲律宾、南非；与中国、印度分列，不代表全部全球南方。','printed':16},
 {'id':4,'title':'中国与美国的贡献交叉','source':'本报告第19页上方地区比较序列；2022—2026报告年度，单位为OpenRank。','boundary':'不与同页下方自然年序列或GitHub单平台国家榜混算；不据此推导全面领先。','printed':19},
 {'id':5,'title':'杭州的模型复用位置','source':'《杭州市开源生态全景报告》（2026年7月），第3、20页；HF快照2026.07.17。','boundary':'北京、上海、深圳、杭州、合肥的机构发布者样本；累计下载不等于用户数，快照属于期后。'},
 {'id':6,'title':'华为与微软的月榜交叉','source':'OpenShare全球发起方月榜：2026年2、3、6月；本报告第41页补充3—6月轨迹。','boundary':'3月华为超过微软；主期全年企业榜仍为微软第1、华为第2，月榜与全年榜分别解释。','url':'https://open-share.com/insight/open-leaderboard?scope=Global&unit=Initiator&timeType=month&time=2026-03&search=&page=1','printed':41},
 {'id':7,'title':'开放原子与Apache的月榜交叉','source':'OpenShare全球基金会月榜：2025年5—7月；LF及其子基金会依报告口径汇总。','boundary':'6月交叉早于主期；LF按14个当前标签回溯相加，标签可重叠，不是仓库去重后的值。','url':'https://open-share.com/insight/open-leaderboard?scope=Global&unit=Foundation&timeType=month&time=2025-06&search=&page=1','printed':44},
 {'id':8,'title':'Agent技术全景中的新创建仓库','source':'本报告第61页；固定全景清单e330d75，观察截至2026.09.27，属期后。','boundary':'AgentInfra的86个项目中，48个仓库创建于2025年以来：48÷86＝55.8%；不是两版名单更替率。','url':'https://github.com/X-lab2017/2026-Global-Open-Source-Development-Report/blob/c51e3441361407b68f10b339d97eff288319b503/preview/content/landscape/data/agentic-ai-projects.csv','printed':61},
]
APP_TITLE='18　年度变化专题：证据与比较口径'
APP_LEAD='对应前置专题xi—xii。八项观察结合年度变化、月度交叉与本版新增视角；各项对象和时间窗口分别保留，不能合成为统一的年度增长率。'
APP_NOTE='本专题沿用主统计期2025.07.01—2026.06.30。历史、外部报告年度与期后快照按各图标注；本页列出比较所需的边界。原始月榜、计算表、固定项目清单与完整来源记录，随本PDF的专题来源附件保存。'
APP_END='其中“55.8%”仅表示固定样本中新创建仓库的比例；2025版与2026版项目名单的逐项更替率尚未核算，不作为本报告结论。'
chars=''.join([BRIDGE,APP_TITLE,APP_LEAD,APP_NOTE,APP_END,'GOSD 2026 全球开源发展报告/ 精要版OPEN SOURCE / A SHARED INTELLIGENT FUTURE','2025—2026：全球开源的八大变化','指标、方法与数据来源附录・模型生态与年度变化供给、派生、开放条件与跨期比较17—18115—116xiivcldm1234567890点击来源名称打开原始材料；点击页码返回正文。']+[a+b for a,b,_ in ENTRIES]+[a['title']+a['source']+a['boundary'] for a in EVIDENCE])
FONTS={}
for name,family,style in [('Regular','Sans','Regular'),('Bold','Sans','Bold'),('Serif','Serif','Bold')]:
 path=SRC/'fonts'/f'Noto{family}CJKsc-{style}.otf'
 font=TTFont(f'/usr/share/fonts/opentype/noto/Noto{family}CJK-{style}.ttc',fontNumber=2)
 opt=subset.Options();opt.retain_gids=True
 sub=subset.Subsetter(options=opt);sub.populate(text=chars);sub.subset(font);font.save(path)
 FONTS[name]=(path,fitz.Font(fontfile=str(path)))

# Preserve the approved miniature emblem exactly at print resolution.
old[136].get_pixmap(matrix=fitz.Matrix(8,8),clip=fitz.Rect(53,23,76,44),alpha=True).save(SRC/'approved-appendix-emblem.png')

def roman(n):
 s=''
 for v,c in [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
  while n>=v:s+=c;n-=v
 return s
def mapped(i):return i if i<12 else i+2
def printed_target(n):return 24+n-1
def spans(p):return [s for b in p.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']]
def write(p,x,y,t,size=10,color=NAVY,style='Regular',right=None):
 path,font=FONTS[style];n='GOSD17'+style;p.insert_font(fontname=n,fontfile=str(path))
 missing=[c for c in t if not c.isspace() and not font.has_glyph(ord(c))]
 assert not missing,('Missing font glyphs',t,missing)
 if right is not None:x=right-font.text_length(t,fontsize=size)
 p.insert_text((x,y),t,fontname=n,fontsize=size,color=color)
def wrap(t,width,size,style='Regular'):
 f=FONTS[style][1];tokens=re.findall(r'[A-Za-z0-9][A-Za-z0-9._/-]*|.',t);lines=[];line=''
 for token in tokens:
  if f.text_length(line+token,fontsize=size)>width and line:
   if token[0] in '，。；：、！？）》】%％':line+=token;lines.append(line);line=''
   else:lines.append(line);line=token
  else:line+=token
 if line:lines.append(line)
 return lines
def para(p,x,y,t,width,size=9.6,leading=14.5,color=NAVY,style='Regular'):
 lines=wrap(t,width,size,style)
 for j,line in enumerate(lines):write(p,x,y+j*leading,line,size,color,style)
 return y+len(lines)*leading
def redact(p,rect):
 p.add_redact_annot(fitz.Rect(rect),fill=False);p.apply_redactions(images=0,graphics=0,text=0)
def folio(p,t):write(p,0,812.967,t,10.4608,NAVY,'Bold',right=544.258)
def header(p,front=True):
 if front:
  write(p,51.024,34.397,'GOSD',10.9589,NAVY,'Serif')
  write(p,133.23,35.073,'2026 全球开源发展报告/ 精要版',7.5716,MUTED)
  p.draw_line((51.0243,51.5911),(544.259,51.5911),color=(.796,.847,.886),width=.59776)
  colors=[(.125,.365,.659),(0,.498,.522),(.153,.482,.314),(.647,.427,.075),(.475,.329,.62)]
  for j,c in enumerate(colors):p.draw_rect(fitz.Rect(459.2185+17.2916*j,50.4572,473.3919+17.2916*j,52.725),color=None,fill=c)
 else:
  # Mirror the appendix running header and footer from printed p.115.
  source=old[136]
  p.insert_image(fitz.Rect(53,23,76,44),filename=str(SRC/'approved-appendix-emblem.png'))
  for s in spans(source):
   if s['bbox'][1]<52 or s['bbox'][1]>789:
    if s['text'].strip()=='115':continue
    c=fitz.sRGB_to_pdf(s['color']);sty='Bold' if 'Bold' in s['font'] else 'Regular'
    write(p,*s['origin'],s['text'],s['size'],c,sty)
  for shape in source.get_drawings():
   if (shape['rect'].y1<52 and shape['rect'].x1>90) or shape['rect'].y0>789:
    for item in shape['items']:
     if item[0]=='l':p.draw_line(item[1],item[2],color=shape['color'],width=shape['width'] or .5)

# The new pages share the exact approved running furniture and native A4 geometry.
new=fitz.open();scale=174/257;ox=(18-20*scale)*MM;oy=6.4*MM
matrix=fitz.Matrix(scale,0,0,scale,ox,oy)
insert_links=[]
for i in range(2):
 p=new.new_page(width=595.28,height=841.89)
 p.insert_image(fitz.Rect(.199,.20752,595.47162,842.10291),stream=old.extract_image(69)['image'],keep_proportion=False)
 p.draw_rect(fitz.Rect(0,0,595.28,781.4),fill=(1,1,1),color=None)
 header(p)
 p.show_pdf_page(art[i].rect*matrix,art,i,keep_proportion=False)
 write(p,51.024,813.421,'OPEN SOURCE / A SHARED INTELLIGENT FUTURE',6.9738)
 folio(p,roman(11+i))
 for link in art[i].get_links():
  n={'kind':link['kind'],'from':link['from']*matrix,'uri':link['uri']};p.insert_link(n)
  insert_links.append({'insert_page':i,**n})
new.set_page_labels([{'startpage':0,'style':'r','firstpagenum':11}])
new.set_metadata({'title':'2025—2026：全球开源的八大变化','author':'全球开源发展报告编写组','subject':'年度变化专题v0.5；COSSI中文全文v1.7，前置xi—xii','creator':'GOSD XeLaTeX and vector page assembly'})
new.save(OUT/'GOSD_2026_八大年度变化_中文两页_v0.5.pdf',garbage=4,deflate=True)

doc=fitz.open();doc.insert_pdf(old,from_page=0,to_page=11,links=False)
doc.insert_pdf(new,links=False);doc.insert_pdf(old,from_page=12,to_page=141,links=False)
assert len(doc)==144
folio_changes=[]
for oi in range(12,21):
 p=doc[mapped(oi)]
 found=[s for s in spans(p) if s['bbox'][0]>500 and s['bbox'][1]>798 and re.fullmatch(r'[ivxlcdm]+',s['text'])]
 assert len(found)==1,(oi,found)
 s=found[0];redact(p,fitz.Rect(s['bbox'])+(-.2,-.2,.2,.2));after=roman(mapped(oi)-1);folio(p,after)
 folio_changes.append({'old_physical':oi+1,'new_physical':mapped(oi)+1,'before':s['text'],'after':after})

# Contents: nine frontmatter rows; the chapter and appendix printed page numbers stay stable.
p=doc[8];redact(p,(49.5,219.5,383,396));contents_rects=[]
for j,(title,folio_text,target) in enumerate(ENTRIES):
 y=232.5+18.4*j
 write(p,51.024,y,title,9.7634)
 write(p,0,y,folio_text,9.7634,MUTED,right=379.848)
 contents_rects.append((fitz.Rect(50,y-12,382,y+4),target,title))

# Bridge from the new annual observations back to the common goals and indicators.
p=doc[14];redact(p,(50,187.5,545,219.0))
bridge_lines=wrap(BRIDGE,493.2,10.3611)
assert len(bridge_lines)==2,bridge_lines
for j,t in enumerate(bridge_lines):write(p,51.024,198.68898+16.937*j,t,10.3611,(36/255,57/255,80/255))

# Reuse the formerly blank appendix page, with no extra physical leaf.
p=doc[printed_target(116)];assert not p.get_text().strip()
header(p,front=False)
write(p,51.024,83,APP_TITLE,18,NAVY,'Bold')
end=para(p,51.024,109,APP_LEAD,493.2,size=9.7,leading=14.3)
assert end<155,end
app_source_rects=[]
for j,e in enumerate(EVIDENCE):
 y=165+j*62
 p.draw_circle((59.5,y-3.5),7,color=None,fill=TEAL)
 write(p,0,y-.4,str(e['id']),8.2,(1,1,1),'Bold',right=61.8)
 write(p,74,y,e['title'],10.6,NAVY,'Bold')
 if e.get('printed'):
  label='正文 '+str(e['printed'])+' 页'
  write(p,0,y,label,8.2,TEAL,right=544.258)
  app_source_rects.append((fitz.Rect(484,y-11,545,y+4),printed_target(e['printed']),'body'))
 source_end=para(p,74,y+15,e['source'],470,size=8.65,leading=12.2,color=NAVY)
 boundary_end=para(p,74,source_end,e['boundary'],470,size=8.65,leading=12.2,color=MUTED)
 assert boundary_end<=y+57,(e['id'],boundary_end,y)
 if e.get('url'):app_source_rects.append((fitz.Rect(73,y+4,544,source_end+1),e['url'],'uri'))
 p.draw_line((51.024,y+48),(544.258,y+48),color=(.84,.89,.92),width=.45)
p.draw_rect(fitz.Rect(51.024,681,544.258,771),color=None,fill=(.949,.966,.973))
write(p,62,698,'时间窗口与比较边界',10.2,TEAL,'Bold')
end=para(p,62,714,APP_NOTE,470,size=8.75,leading=12.5,color=NAVY)
end=para(p,62,end+3,APP_END,470,size=8.75,leading=12.5,color=NAVY)
assert end<=772,end
write(p,0,818.82495,'116',10.460695,fitz.sRGB_to_pdf(533596),'Bold',right=564.09589)

# Update appendix opening guide, without changing any existing section destinations.
guide=doc[printed_target(97)];replacements={'17':'17—18','模型生态方法':'模型生态与年度变化','供给、派生、开放条件与证据范围':'供给、派生、开放条件与跨期比较','115':'115—116'}
guide_changes=[]
for before,after in replacements.items():
 found=[s for s in spans(guide) if s['text'].strip()==before]
 assert len(found)==1,(before,found)
 s=found[0];redact(guide,fitz.Rect(s['bbox'])+(-.15,-.15,.15,.15))
 style='Bold' if 'Bold' in s['font'] else 'Regular'
 x,y=s['origin'];right=s['bbox'][2] if before=='115' else None
 write(guide,x,y,after,s['size'],fitz.sRGB_to_pdf(s['color']),style,right=right)
 guide_changes.append({'before':before,'after':after,'rect':list(s['bbox'])})

# Explicitly rebuild every destination after insertion; URI and mail links are retained.
links=[]
def add_link(pi,link,origin):
 n={'kind':link['kind'],'from':fitz.Rect(link['from'])}
 if n['kind']==fitz.LINK_GOTO:
  n.update(page=link['page'],to=fitz.Point(link.get('to',(0,0))),zoom=link.get('zoom',0));assert 0<=n['page']<len(doc)
 elif n['kind']==fitz.LINK_URI:n['uri']=link['uri']
 else:raise ValueError(link)
 doc[pi].insert_link(n)
 links.append({'physical_page':pi+1,'kind':n['kind'],'rect':list(n['from']),'target_physical':n.get('page',-1)+1,'uri':n.get('uri'),'origin':origin})
for oi,p in enumerate(old):
 for link in p.get_links():
  if oi==8 and link['from'].x1<390 and 215<link['from'].y0<400:continue
  n=dict(link)
  if n['kind']==fitz.LINK_GOTO:n['page']=mapped(n['page'])
  add_link(mapped(oi),n,'v1.6 original; destination remapped')
for rect,target,title in contents_rects:add_link(8,{'kind':1,'from':rect,'page':target},'Frontmatter contents: '+title)
for n in insert_links:add_link(12+n['insert_page'],n,'Annual-change official source')
for rect,target,kind in app_source_rects:
 add_link(printed_target(116),{'kind':2,'from':rect,'uri':target} if kind=='uri' else {'kind':1,'from':rect,'page':target},'Annual-change evidence index')
# Each new panel's source strip opens its precise evidence-index row.
for i in range(2):
 for j in range(4):
  x=20+(j%2)*132.5;y=88+(j//2)*86
  target_y=150+(i*4+j)*62
  add_link(12+i,{'kind':1,'from':fitz.Rect(x*MM,(y+13.4)*MM,(x+124.5)*MM,(y+22)*MM)*matrix,'page':printed_target(116),'to':(51,target_y)},'Panel source → evidence index '+str(i*4+j+1))
 for rect in doc[12+i].search_for('完整口径见附录第116页'):
  add_link(12+i,{'kind':1,'from':rect,'page':printed_target(116)},'Annual-change footer → evidence index')
add_link(printed_target(116),{'kind':1,'from':fitz.Rect(50,96,545,151),'page':12},'Evidence index → annual-change insert')
# Additional entry in the appendix guide and visible reference in the framework paragraph.
for rect in guide.search_for('115—116'):add_link(printed_target(97),{'kind':1,'from':rect,'page':printed_target(115)},'Appendix guide: methods and annual changes')

toc=[]
for item in old.get_toc(False):
 level,title,physical,dest=item;dest=copy.deepcopy(dest);dest.pop('xref',None)
 if physical>0:physical=mapped(physical-1)+1
 if dest.get('kind')==1 and dest.get('page',-1)>=0:dest['page']=mapped(dest['page'])
 toc.append([level,title,physical,dest])
 if title=='从发现到行动':
  toc.extend([[2,'2025—2026：全球开源的八大变化',13],[3,'开发加速、资产扩展与全球南方成长',13],[3,'城市、企业、基金会与Agent技术生态',14]])
# Place the new appendix topic immediately before acknowledgements.
idx=next(i for i,t in enumerate(toc) if t[2]==printed_target(117)+1)
toc.insert(idx,[2,APP_TITLE,printed_target(116)+1])
doc.set_toc(toc,collapse=1)
doc.set_page_labels([{'startpage':0,'prefix':'Cover'},{'startpage':1,'prefix':'Inside cover'},
 {'startpage':2,'style':'r','firstpagenum':1},{'startpage':23,'prefix':'Blank'},
 {'startpage':24,'style':'D','firstpagenum':1},{'startpage':142,'prefix':'Inside back cover'},{'startpage':143,'prefix':'Back cover'}])
doc.set_pagemode('UseOutlines')
doc.set_metadata({'title':'2026 全球开源发展报告（精要版）- COSSI中文版 v1.7','author':'全球开源发展报告编写组；序言：王伟','subject':'144页；年度变化专题精修并入xi—xii；目录、前置页码、导航及附录证据索引同步更新','keywords':'GOSD,2026,精要版,COSSI,CCOSI,年度变化,AI,OSDGs,OSDI','creator':'GOSD 2026 Report Assembly','producer':'GOSD PDF-first workflow','modDate':'D:20261118000000Z'})
for name in old.embfile_names():
 info=old.embfile_info(name)
 doc.embfile_add(name,old.embfile_get(name),filename=info.get('filename',name),desc=info.get('desc','Approved historical build source'))

manifest={'version':'COSSI zh-CN v1.7','insert_version':'v0.5','date':'2026-11-18','status':'rebuild from author-approved Chinese v1.7 sources',
 'baseline':{'file':BASE.name,'sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'pages':142},
 'output_pages':144,'placement':'after 从发现到行动, before 一套共同的观察语言','new_physical_pages':[13,14],'new_printed_pages':['xi','xii'],
 'body_printed_pages':'1—118','body_physical_pages':[25,142],'appendix_evidence_printed_page':116,'appendix_evidence_physical_page':140,
 'contents_physical_page':9,'frontmatter_printed_pages':'i—xxi','changed_existing_pages':[9,13,14,15,16,17,18,19,20,21,119,138],
 'changed_existing_pages_explanation':'Physical pages of v1.6. Page 9 contents; 13 transition and folio; 14—21 folios; 119 appendix guide; 138 formerly blank evidence page.',
 'folio_changes':folio_changes,'contents_entries':[{'label':a,'folio':b,'target_physical':c+1} for a,b,c in ENTRIES],
 'bridge':{'physical_page':15,'text':BRIDGE},'appendix_guide_changes':guide_changes,
 'navigation':{'bookmarks':len(toc),'links':len(links),'internal_links':sum(x['kind']==1 for x in links),'external_links':sum(x['kind']==2 for x in links)},
 'pending':['2025 and 2026 landscape membership turnover has not been calculated; 55.8% is explicitly a repository-creation cohort share.','Existing report verification limitations are inherited, not certified by this layout integration.'],
 'review_focus':['continuity from executive summary to annual changes and common framework','A4 readability of the eight panels','new appendix source index and navigation']}
(SRC/'assembly-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(SRC/'navigation-links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2))
(SRC/'navigation-bookmarks.json').write_text(json.dumps(toc,ensure_ascii=False,indent=2,default=list))
(SRC/'evidence-index.json').write_text(json.dumps(EVIDENCE,ensure_ascii=False,indent=2))
doc.embfile_add('COSSI_ZH_v1.7_Assembly_Record.json',json.dumps(manifest,ensure_ascii=False,indent=2).encode(),filename='COSSI_ZH_v1.7_Assembly_Record.json',desc='Current integration, page mapping, evidence boundaries and navigation record')
pack=OUT/'Annual_Changes_v0.5_Evidence_and_Source.zip'
with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED) as z:
 for folder in [R/'insert/source',R/'insert/evidence',SRC,R/'evidence']:
  for file in sorted(folder.rglob('*')):
   if file.is_file() and file.suffix not in ['.js','.html','.pyc','.otf'] and '__pycache__' not in file.parts:z.write(file,file.relative_to(R))
doc.embfile_add(pack.name,pack.read_bytes(),filename=pack.name,desc='Annual-change editable source, source records, original monthly tables and cohort calculations')
target=OUT/'GOSD_2026_Essential_COSSI_zh-CN_v1.7.pdf'
doc.save(target,garbage=4,deflate=True)
print(json.dumps({'file':str(target),'pages':len(doc),'bytes':target.stat().st_size,**manifest['navigation']},ensure_ascii=False))
