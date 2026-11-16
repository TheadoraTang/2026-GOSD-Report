from pathlib import Path
import json, argparse

parser = argparse.ArgumentParser()
parser.add_argument('--work-dir', required=True)
ROOT = Path(parser.parse_args().work_dir).resolve()
SRC = ROOT/'source'
OUT = ROOT/'output'
OUT.mkdir(exist_ok=True)
board = json.loads((ROOT/'content/editorial_board.json').read_text())
intro = json.loads((ROOT/'content/ccosi_intro_zh.json').read_text())
W,H = 595.276,841.890
parts = [r'''\documentclass[a4paper]{article}
\usepackage[margin=0pt]{geometry}
\usepackage{fontspec,xeCJK,graphicx,tikz,xcolor}
\usetikzlibrary{fadings}
\setmainfont{TeX Gyre Termes}
\setsansfont{Noto Sans}
\setCJKmainfont{Noto Serif CJK SC}
\setCJKsansfont{Noto Sans CJK SC}
\setlength{\parindent}{0pt}
\pagestyle{empty}
\definecolor{ink}{HTML}{102B50}
\definecolor{body}{HTML}{243950}
\definecolor{blue}{HTML}{205DA8}
\definecolor{muted}{HTML}{596E82}
\definecolor{teal}{HTML}{007F85}
\definecolor{rule}{HTML}{CFDCE7}
\definecolor{covernavy}{HTML}{203468}
\tikzfading[name=bandfade,top color=transparent!100,bottom color=transparent!0]
\begin{document}
''']
pages=[]

def text(x,y,w,t,size=11,leading=19,font='serif',color='body',bold=False):
    pages[-1].append(dict(type='text',x=x,y=y,w=w,text=t.replace('\\\\','\n'),size=size,leading=leading,font=font,color=color,bold=bold))
    fam = r'\sffamily' if font=='sans' else r'\rmfamily'
    weight = r'\bfseries' if bold else r'\mdseries'
    parts.append(r'\node[anchor=north west,inner sep=0pt,outer sep=0pt,text width=%sbp,align=justify,text=%s] at (%s,%s) {%s%s\fontsize{%sbp}{%sbp}\selectfont %s};' % (w,color,x,y,fam,weight,size,leading,t))

def line(x,y,x2,color='rule',width=.6):
    pages[-1].append(dict(type='line',x=x,y=y,x2=x2,color=color,width=width))
    parts.append(r'\draw[%s,line width=%sbp] (%s,%s)--(%s,%s);' % (color,width,x,y,x2,y))

def circle(x,y,r,fill,stroke=None):
    pages[-1].append(dict(type='circle',x=x,y=y,r=r,fill=fill,stroke=stroke,width=.7))

def segment(x,y,x2,y2,color='rule',width=.8):
    pages[-1].append(dict(type='line',x=x,y=y,x2=x2,y2=y2,color=color,width=width))

def centertext(x,y,w,t,size=8.5,leading=12,bold=False,color='ink'):
    text(x,y,w,t,size,leading,'sans',color,bold)
    pages[-1][-1]['align']='center'

def begin():
    pages.append([])
    parts.append(r'\null\begin{tikzpicture}[remember picture,overlay,x=1bp,y=-1bp,shift={(current page.north west)}]')

def end(last=False):
    parts.append(r'\end{tikzpicture}'+('' if last else r'\newpage'))

def common(folio):
    begin()
    # Reuse only the decorative footer strip of the approved page. Its old text is covered.
    parts.append(r'\begin{scope}\clip (0,781) rectangle (595.276,841.89);\node[anchor=north west,inner sep=0] at (0,0) {\includegraphics[width=595.276bp,height=841.89bp]{assets/body-baseline.pdf}};\end{scope}')
    parts.append(r'\fill[white] (0,801) rectangle (595.276,841.89);')
    # A restrained white footer leaves the retained wave as the continuous visual cue.
    text(51,25,70,'GOSD',11,12,'serif','ink',True)
    text(133,28,290,'2026 全球开源发展报告 / 精要版',7.6,9,'sans','muted')
    line(51,51.7,544)
    for i,c in enumerate(['205DA8','24A9C6','4B9F73','C89C25','8660A6']):
        parts.append(r'\definecolor{accent}{HTML}{%s}\draw[accent,line width=1.8bp] (%s,51.7)--(%s,51.7);' % (c,459+i*17.1,472.7+i*17.1))
    text(51,808,400,'OPEN SOURCE / A SHARED INTELLIGENT FUTURE',6.6,8,'sans','ink')
    text(529,805,16,folio,10,12,'sans','ink',True)

def title(kicker,zh,en):
    text(51,75,493,kicker,8,10,'sans','blue',True)
    text(51,101,493,zh,25,34,'serif','ink',True)
    text(51,145,493,en,9,12,'sans','muted')

def section(y,label):
    text(51,y,130,label,10.5,14,'sans','teal',True)
    line(188,y+7,544)

# 1: Cover. Existing upper cover is unchanged; institutional band is independently editable.
begin()
parts.append(r'\node[anchor=north west,inner sep=0] at (0,0) {\includegraphics[width=595.276bp,height=841.89bp]{assets/cover-baseline.png}};')
parts.append(r'\fill[covernavy,path fading=bandfade] (0,742) rectangle (595.276,766);')
parts.append(r'\fill[covernavy] (0,765.9) rectangle (595.276,841.89);')
parts.append(r'\node[anchor=north west,inner sep=0] at (176.888,773.1) {\includegraphics[width=75bp]{assets/ccosi.png}};')
parts.append(r'\node[anchor=north west,inner sep=0] at (289.888,772) {\includegraphics[width=128.5bp,trim=17 70 18 69,clip]{assets/siri-white.png}};')
for i,c in enumerate(['5C9FF1','72D4E5','72D5B9','A3D758','D5D343','EBC94C','F0934D','DE5A95','A361DE','7E52DD']):
    parts.append(r'\definecolor{accent}{HTML}{%s}\draw[accent,line width=2bp] (%s,831)--(%s,831);' % (c,53+i*49.2,99+i*49.2))
end()

# 2: Replacement for physical p3 / folio i.
common('i')
text(51,75,493,'关于本报告 / ABOUT THIS REPORT',8,10,'sans','blue',True)
text(51,104,493,'2026',21,25,'serif','blue')
text(51,143,493,'全球开源发展报告',31,40,'serif','ink',True)
text(51,194,493,'Global Open Source Development Report',13,17,'serif','muted')
text(51,226,493,'精要版 / ESSENTIAL EDITION',9,12,'sans','blue',True)
line(51,258,544)
text(51,284,493,'开放协作，共创未来',20,28,'serif','ink',True)
text(51,327,493,'开放资源怎样转化为可持续公共能力？',16.8,24,'serif','teal',True)
text(51,378,493,'人工智能正在改变资源的生产、传播与使用。开源连接开发者、研究机构、企业与公共部门，使代码、模型和数据能够被持续使用与改进，也为不同地区参与创新提供新的机会。',11,19)
text(51,458,493,'本报告以开源发展目标（OSDGs）、指标体系（OSDI）与评价数据结构为共同参考，联读生态地图、主体榜单、技术全景与模型网络。我们希望各类组织通过实际采用、独立复核与共同改进，让评价方法服务于发展决策。',11,19)
line(51,556,544)
for y,label,val in [
    (579,'研究对象','开发者、组织、项目，以及代码、模型、数据及其协作关系。'),
    (616,'主统计期','2025 年 7 月 1 日—2026 年 6 月 30 日。'),
    (653,'时间说明','历史比较、外部统计窗口与期后观察分别标明，以各图为准。'),
    (690,'阅读与使用','面向政府、国际组织、企业、学术机构、基金会与开源社区。')]:
    text(51,y,80,label,9.4,13,'sans','blue',True)
    text(139,y,405,val,10,15,'sans')
text(51,743,493,'框架、指标与数据持续更新；年度结论按所标注版本与时间窗口使用。',8.4,13,'sans','muted')
end()

# 3: Replacement for editorial board. All names exactly 11bp, regular, same font.
common('ii')
title('共同编写','编委会','Editorial Board')
for y,head,key in [(200,'顾问','advisors'),(294,'主任','directors'),(388,'副主任','deputies')]:
    section(y,head)
    for i,name in enumerate(board[key]):
        x=51+i*(82.2 if key=='deputies' else 164.4)
        text(x,y+37,79,name,11,15,'sans','ink')
section(493,'编委')
for i,name in enumerate(board['members']):
    row,col=divmod(i,10)
    text(51+49.32*col,533+39*row,46.5,name,11,15,'sans','ink')
end()

# 4: Committee introduction, first page. Photo is clipped in the PDF, no pixel retouching.
common('iii')
text(51,75,493,'专委会介绍 / ABOUT CCOSI',8,10,'sans','blue',True)
text(51,96,493,r'中国科协联合国咨商\\开源创新专委会',23,29,'serif','ink',True)
text(51,165,493,'CAST UN Consultative Committee on Open Source Innovation (CCOSI)',8.3,11,'sans','muted')
text(51,191,493,intro['sections'][0]['paragraphs'][0],10.4,17)
parts.append(r'\node[anchor=north west,inner sep=0] at (51,260) {\includegraphics[width=493bp,trim=0 150 0 330,clip]{assets/committee-photo.jpg}};')
text(51,477,493,intro['photo_caption'],8,11,'sans','muted')
text(51,508,290,'核心职能',10.5,14,'sans','teal',True)
line(116,515,330)
text(51,535,280,intro['sections'][1]['paragraphs'][0],10.4,17)
# Secretariat coordination, redrawn as native elements from the supplied diagram.
for xx,yy in [(453,532),(397,634),(509,634)]:
    segment(453,584,xx,yy,'9EC8CC',1.1)
circle(453,584,24,'007F85')
centertext(429,579,48,'秘书处',10,12,True,'FFFFFF')
for xx,yy,fill,label in [(453,532,'EBF5FA',r'智库与政策\\研究组'),(397,634,'EDF5EF',r'数字公共品\\推进组'),(509,634,'E6F4F3',r'标准与国际\\合作组')]:
    circle(xx,yy,29,fill,'A5C9CD')
    centertext(xx-29,yy-10,58,label,8.3,12,True)
section(681,'组织架构与运行机制')
text(51,705,493,intro['sections'][2]['paragraphs'][0],10.2,16)
end()

# 5: Committee introduction, second page.
common('iv')
title('专委会介绍 / CCOSI','开源创新与国际合作','Open Source Innovation and International Cooperation')
# Native diagram elements are populated from the editable SVG/JSON reference.
diagram=json.loads((SRC/'assets/ccosi-work-system.json').read_text())
for o in diagram['elements']:
    n=dict(o)
    if n['type']=='line':
        n['x']=n.pop('x1');n['y']=n.pop('y1');n['width']=n.get('stroke_width',.7)
    if n['type']=='text':
        n['font']='sans';n['bold']=n.get('weight',400)>=600
        n['w']=493;n['leading']=n['size']*1.25;n['no_wrap']=True
    for key,offset in [('x',51),('y',184),('x2',51),('y2',184)]:
        if key in n:n[key]+=offset
    if 'points' in n:n['points']=[[x+51,y+184] for x,y in n['points']]
    pages[-1].append(n)
text(51,499,493,'技术支撑、治理引导、实践传播与发展评价相互衔接。',8.7,12,'sans','muted')
for y,idx in [(535,3),(653,4)]:
    section(y,intro['sections'][idx]['heading'])
    text(51,y+25,493,intro['sections'][idx]['paragraphs'][0],10.7,17.5)
pages[-1].append(dict(type='rect',x=51,y=742,w=493,h=33,fill='EDF5F8'))
text(62,752,75,'联系专委会',9.2,12,'sans','teal',True)
text(144,747,388,'秘书长：王伟 · 华东师范大学数据学院',9.3,12,'sans','ink')
text(144,761,388,'wwang@dase.ecnu.edu.cn',9.3,12,'sans','blue')
end(last=True)
parts.append(r'\end{document}')
(SRC/'frontmatter.tex').write_text('\n'.join(parts))
(SRC/'layout.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2))
print(SRC/'layout.json')
