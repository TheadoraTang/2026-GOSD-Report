"""Render exact A4 review pages. All new text remains native, with embedded SC fonts.

The companion .tex preserves a Chinese-friendly LaTeX layout for later integration.
This renderer does not need a full TeX installation. Images are unmodified inputs;
photo cropping and the replacement cover band are document layout operations.
"""
from pathlib import Path
import json, re, fitz, hashlib, argparse
from fontTools import subset
from fontTools.ttLib import TTFont

parser=argparse.ArgumentParser()
parser.add_argument('--work-dir',required=True)
args=parser.parse_args()
ROOT=Path(args.work_dir).resolve()
S=ROOT/'source'
OUT=ROOT/'output'
QA=ROOT/'qa';QA.mkdir(exist_ok=True)
pages=json.loads((S/'layout.json').read_text())
allchars=''.join(o.get('text','') for page in pages for o in page)
charset_hash=hashlib.sha256(''.join(sorted(set(allchars))).encode()).hexdigest()
cachefile=S/'fonts'/'charset.sha256'
cache_matches=cachefile.exists() and cachefile.read_text().strip()==charset_hash
fonts={}
(S/'fonts').mkdir(exist_ok=True)
for fam in ['sans','serif']:
    for bold in [False,True]:
        name=f'{fam}-'+('bold' if bold else 'regular')
        path=S/'fonts'/f'{name}.otf'
        if not path.exists() or not cache_matches:
            original=ROOT/'font-inputs'/('Noto'+fam.title()+'CJK-'+('Bold' if bold else 'Regular')+'.ttc')
            f=TTFont(original,fontNumber=2)
            opt=subset.Options(); opt.name_IDs=['*'];opt.name_legacy=True;opt.name_languages=['*'];opt.retain_gids=True
            sub=subset.Subsetter(options=opt);sub.populate(text=allchars);sub.subset(f);f.save(path)
        fonts[(fam,bold)]=(name,path,fitz.Font(fontfile=str(path)))
cachefile.write_text(charset_hash+'\n')

C={'ink':'102B50','body':'243950','blue':'205DA8','muted':'596E82','teal':'007F85','rule':'CFDCE7','covernavy':'203468'}
def color(s):
    s=C.get(s,s).lstrip('#');return tuple(int(s[i:i+2],16)/255 for i in (0,2,4))

doc=fitz.open()
bg=fitz.open(S/'assets/body-baseline.pdf')
photo=fitz.open();im=fitz.Pixmap(str(S/'assets/committee-photo.jpg'))
pp=photo.new_page(width=im.width,height=im.height);pp.insert_image(pp.rect,filename=str(S/'assets/committee-photo.jpg'))
siri=fitz.open();sp=siri.new_page(width=2048,height=546);sp.insert_image(sp.rect,filename=str(S/'assets/siri-white.png'))
rendered=[]

def wrap(t,font,size,width):
    # ASCII words stay intact; Chinese punctuation cannot begin the following line.
    toks=re.findall(r'[A-Za-z0-9]+(?:[ ./—-][A-Za-z0-9]+)*|[^A-Za-z0-9]',t)
    lines=[]; cur=''
    closing='，。；：？！、）】》”’％%'
    for tok in toks:
        if tok=='\n':lines.append(cur);cur='';continue
        if font.text_length(cur+tok,fontsize=size)>width and cur:
            if tok in closing:
                carry=cur[-1];cur=cur[:-1];lines.append(cur.rstrip());cur=carry+tok
            else:lines.append(cur.rstrip());cur=tok.lstrip()
        else:cur+=tok
    if cur:lines.append(cur.rstrip())
    return lines

for idx,ops in enumerate(pages):
    page=doc.new_page(width=595.276,height=841.89)
    if idx==0:
        page.insert_image(page.rect,filename=str(S/'assets/cover-baseline.png'))
        for k in range(120):
            y=742+k*.2
            page.draw_rect(fitz.Rect(0,y,595.276,y+.25),fill=color('covernavy'),color=None,fill_opacity=(k+1)/120,overlay=True)
        page.draw_rect(fitz.Rect(0,766,595.276,841.89),fill=color('covernavy'),color=None,overlay=True)
        page.insert_image(fitz.Rect(176.888,773.1,251.888,773.1+75*225/568),filename=str(S/'assets/ccosi.png'))
        page.show_pdf_page(fitz.Rect(289.888,772,418.388,772+128.5*407/2013),siri,0,clip=fitz.Rect(17,69,2030,476))
        for i,c in enumerate(['5C9FF1','72D4E5','72D5B9','A3D758','D5D343','EBC94C','F0934D','DE5A95','A361DE','7E52DD']):
            page.draw_line((53+i*49.2,831),(99+i*49.2,831),color=color(c),width=2)
    else:
        clip=fitz.Rect(0,781,595.276,801)
        page.show_pdf_page(clip,bg,0,clip=clip)
        for i,c in enumerate(['205DA8','24A9C6','4B9F73','C89C25','8660A6']):
            page.draw_line((459+i*17.1,51.7),(472.7+i*17.1,51.7),color=color(c),width=1.8)
    if idx==3:
        clip=fitz.Rect(0,330,im.width,im.height-150)
        rect=fitz.Rect(51,260,544,260+493*clip.height/clip.width)
        page.show_pdf_page(rect,photo,0,clip=clip)
    for fam,bold in fonts:
        name,path,f=fonts[(fam,bold)];page.insert_font(fontname=name,fontfile=str(path))
    pageinfo=[]
    for o in ops:
        if o['type']=='line':
            page.draw_line((o['x'],o['y']),(o['x2'],o.get('y2',o['y'])),color=color(o['color']),width=o.get('width',.7))
        elif o['type']=='circle':
            page.draw_circle((o['x'],o['y']),o['r'],fill=color(o['fill']),color=color(o['stroke']) if o.get('stroke') else None,width=o.get('width',.7))
        elif o['type']=='rect':
            page.draw_rect(fitz.Rect(o['x'],o['y'],o['x']+o['w'],o['y']+o['h']),fill=color(o['fill']) if o.get('fill') else None,color=color(o['stroke']) if o.get('stroke') else None,width=o.get('width',.7))
        elif o['type']=='polygon':
            shape=page.new_shape();shape.draw_polyline(o['points']+[o['points'][0]]);shape.finish(fill=color(o['fill']),color=color(o['stroke']) if o.get('stroke') else None);shape.commit()
        else:
            name,path,f=fonts[(o['font'],o['bold'])]
            lines=[o['text']] if o.get('no_wrap') else wrap(o['text'],f,o['size'],o['w'])
            for i,t in enumerate(lines):
                # Top coordinates refer to the visible glyph box; CJK baseline sits 0.88em lower.
                y=o['y']+(0 if o.get('baseline')=='alphabetic' else .88*o['size'])+i*o['leading']
                x=o['x']
                if o.get('align')=='center':x+=(o['w']-f.text_length(t,fontsize=o['size']))/2
                if o.get('anchor')=='middle':x-=f.text_length(t,fontsize=o['size'])/2
                page.insert_text((x,y),t,fontname=name,fontsize=o['size'],color=color(o['color']))
                pageinfo.append({'text':t,'x':o['x'],'y':y,'size':o['size'],'width':f.text_length(t,fontsize=o['size'])})
    rendered.append(pageinfo)
    if idx==4:
        page.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(144,759,265,774),'uri':'mailto:wwang@dase.ecnu.edu.cn'})
doc.set_metadata({'title':'2026 全球开源发展报告·COSSI版前置页 · v1.6重建','author':'GOSD 2026 编写组','subject':'获批v1.6前置页原生重建；封面按主文字光学对齐'})
doc.set_toc([[1,'封面',1],[1,'关于本报告',2],[1,'编委会',3],[1,'专委会介绍',4],[2,'开源创新与国际合作',5]])
target=OUT/'frontmatter.pdf';doc.save(target,garbage=4,deflate=True)
(QA/'rendered-lines.json').write_text(json.dumps(rendered,ensure_ascii=False,indent=2))
print(target)
