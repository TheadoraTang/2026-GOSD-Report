"""Check pagination, navigation, text completeness and preservation of source pages."""
from pathlib import Path
import fitz,json,hashlib,re,collections
import numpy as np
R=Path(__file__).resolve().parents[1]; Q=R/'qa';Q.mkdir(exist_ok=True)
base=fitz.open(R/'inputs/GOSD_2026_Essential_COSSI_zh-CN_v1.6.pdf')
path=R/'output/GOSD_2026_Essential_COSSI_zh-CN_v1.7.pdf';doc=fitz.open(path)
manifest=json.loads((R/'source/assembly-manifest.json').read_text())
errors=[]; stats={}
def check(condition,message):
 if not condition:errors.append(message)
def mapped(i):return i if i<12 else i+2
def normalize(s):return re.sub(r'\s+','',s).replace('・','·').replace('‑','-')
check(len(doc)==144,'Expected 144 pages')
check(all(abs(p.rect.width-595.28)<.01 and abs(p.rect.height-841.89)<.01 for p in doc),'Every page must remain A4 portrait')
check(doc[12].get_label()=='xi' and doc[13].get_label()=='xii','Insert labels xi, xii')
check(doc[22].get_label()=='xxi' and doc[23].get_label()=='Blank','Frontmatter ends at xxi then blank')
check([doc[i].get_label() for i in range(24,142)]==[str(i) for i in range(1,119)],'Body labels remain 1—118')
check('wwang@dase.ecnu.edu.cn' in doc[5].get_text(),'Approved secretary-general contact retained')

# Match complete prose against its structured source, not only a handful of keywords.
content=json.loads((R/'insert/source/content.json').read_text())
for i,c in enumerate(content['pages']):
 text=normalize(doc[12+i].get_text())
 for field in [c['lead'],c['subtitle']]+[it[k] for it in c['items'] for k in ['title','body']]:
  check(normalize(field) in text,'Missing insert text: '+field[:45])
 check('完整口径见附录第116页' in text,'Appendix pointer present')
 check('\ufffd' not in text and '\u25a1' not in text,'No replacement characters in insert')
check(normalize(manifest['bridge']['text']) in normalize(doc[14].get_text()),'Framework transition matches approved assembly source')

# Every inherited bookmark and link must still reach the same logical destination.
original_marks=collections.Counter((t[0],t[1],mapped(t[2]-1)+1) for t in base.get_toc())
current_marks=collections.Counter(tuple(t) for t in doc.get_toc())
check(not (original_marks-current_marks),'Original bookmarks preserved')
check(len(doc.get_toc())==127,'127 bookmarks expected')
for t in doc.get_toc():check(1<=t[2]<=len(doc),'Bookmark target outside report: '+t[1])
link_count=0;internal=0;external=0;retained=0
def link_sig(l,remap=False):
 r=tuple(round(v,2) for v in l['from']);k=l['kind']
 if k==1:return (k,r,mapped(l['page']) if remap else l['page'],tuple(round(v,2) for v in l.get('to',(0,0))),round(l.get('zoom',0),2))
 if k==2:return (k,r,l['uri'])
 return (k,r)
for oi,p in enumerate(base):
 target=doc[mapped(oi)].get_links()
 for l in p.get_links():
  if oi==8 and l['from'].x1<390 and 215<l['from'].y0<400:continue
  # Tiny serialization differences under 0.02 point are not destination changes.
  found=[]
  for n in target:
   if l['kind']!=n['kind'] or max(abs(a-b) for a,b in zip(l['from'],n['from']))>.03:continue
   if l['kind']==1 and n['page']==mapped(l['page']) and max(abs(a-b) for a,b in zip(l.get('to',(0,0)),n.get('to',(0,0))))<.03:found.append(n)
   if l['kind']==2 and l['uri']==n['uri']:found.append(n)
  check(bool(found),f'Lost original link on baseline physical {oi+1}: {link_sig(l)}')
  retained+=bool(found)
for p in doc:
 for l in p.get_links():
  link_count+=1
  check(p.rect.contains(l['from']),'Link outside page '+str(p.number+1))
  if l['kind']==1:
   internal+=1;check(0<=l['page']<len(doc),'Internal link out of range')
  elif l['kind']==2:external+=1;check(bool(l.get('uri')),'Empty external link')
check(link_count==manifest['navigation']['links'],'Link count matches manifest')
stats['navigation']={'bookmarks':len(doc.get_toc()),'links':link_count,'internal':internal,'external':external,'original_links_retained':retained,'original_contents_rows_replaced':8}

# Render all 142 inherited pages once. Only 12 intentional edits may differ.
changed=set(manifest['changed_existing_pages']);pixel_identical=[];localized=[];differences=[]
for oi,op in enumerate(base):
 npg=doc[mapped(oi)];a=op.get_pixmap(alpha=False);b=npg.get_pixmap(alpha=False)
 check((a.width,a.height)==(b.width,b.height),'Inherited page geometry changed')
 aa=np.frombuffer(a.samples,np.uint8).reshape(a.height,a.width,a.n);bb=np.frombuffer(b.samples,np.uint8).reshape(b.height,b.width,b.n)
 diff=np.any(aa!=bb,axis=2)
 if oi+1 not in changed:
  check(not diff.any(),'Unexpected pixel change on baseline physical '+str(oi+1))
  if not diff.any():pixel_identical.append(oi+1)
 else:
  mask=np.zeros(diff.shape,bool)
  regions=[]
  if oi==8:regions=[fitz.Rect(48,218,385,398)]
  elif oi==12:regions=[fitz.Rect(49,186,547,221),fitz.Rect(500,796,548,820)]
  elif 13<=oi<=20:regions=[fitz.Rect(500,796,548,820)]
  elif oi==118:
   for c in manifest['appendix_guide_changes']:
    regions.append(fitz.Rect(c['rect'])+(-3,-3,3,3))
    regions.extend(r+(-3,-3,3,3) for r in npg.search_for(c['after']))
  elif oi==137:regions=[op.rect]
  for r in regions:
   x0=max(0,int(r.x0));y0=max(0,int(r.y0));x1=min(a.width,int(r.x1)+2);y1=min(a.height,int(r.y1)+2)
   mask[y0:y1,x0:x1]=True
  outside=diff & ~mask
  check(not outside.any(),'Pixel change outside authorized region on baseline physical '+str(oi+1))
  if not outside.any():localized.append(oi+1)
  differences.append({'baseline_physical':oi+1,'new_physical':mapped(oi)+1,'changed_pixels':int(diff.sum()),'outside_authorized_region':int(outside.sum())})
stats['page_preservation']={'inherited_pages':142,'pixel_identical_pages':len(pixel_identical),'localized_edits':len(localized),'differences':differences}

# Newly typeset text stays inside the trim and has embedded fonts.
new_pages=[12,13,139];font_refs=set();font_results=[]
for pi in new_pages:
 p=doc[pi]
 for block in p.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   for s in line['spans']:
    check(p.rect.contains(fitz.Rect(s['bbox'])),'Text outside A4 trim: '+s['text'])
 for f in p.get_fonts(full=True):font_refs.add(f[0])
 for s in p.get_text('rawdict')['blocks']:
  for l in s.get('lines',[]):
   for span in l['spans']:
    for c in span['chars']:check(c['c']!='\ufffd','Replacement glyph on new page')
for xref in sorted(font_refs):
 name,ext,kind,data=doc.extract_font(xref)
 font_results.append({'xref':xref,'name':name,'format':ext,'bytes':len(data)})
 check(bool(data),'Unembedded new-page font: '+name)
stats['new_page_fonts']=font_results
stats['source_attachments']=doc.embfile_names()
check(len(stats['source_attachments'])==5,'Preserve 3 historical attachments plus 2 current records')

# Contact sheets and close views are a separate visual review, not a substitute for checks.
for i in [0,8,11,12,13,14,22,24,120,138,139,140,143]:
 doc[i].get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(Q/f'final-{i+1:03d}.png')
stats.update({'version':'COSSI zh-CN v1.7','pages':len(doc),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'errors':errors,'passed':not errors})
(Q/'verification.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in stats.items() if k not in ['new_page_fonts','source_attachments']},ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
