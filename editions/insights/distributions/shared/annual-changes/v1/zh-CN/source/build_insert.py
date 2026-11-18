from pathlib import Path
import json,re,math
R=Path(__file__).resolve().parents[1]
for folder in [R/'qa',R/'output']:folder.mkdir(parents=True,exist_ok=True)
C=json.loads((R/'source/content.json').read_text());D=json.loads((R/'source/chart-data.json').read_text())
L={r['name']:r['file'] for r in json.loads((R/'source/assets/logos.json').read_text())}
T=[];records=[];page=0
GH='https://github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents/'
HF='https://huggingface.co/blog/state-of-open-models-summer-2026'
def esc(s):return str(s).replace('&',r'\&').replace('%',r'\%').replace('_',r'\_').replace('#',r'\#')
def text(x,y,w,s,size=12.5,leading=18.2,color='body',bold=False,serif=False,align='left',raw=False):
 size=max(size,9.0);leading=max(leading,size*1.22)
 val=s if raw else esc(s);font=('\\serif ' if serif else '')+('\\bfseries ' if bold else '')
 al={'left':r'\raggedright ','center':r'\centering ','right':r'\raggedleft '}[align]
 T.append(r'\node[anchor=north west,inner sep=0,text='+color+'] at ('+f'{x},{y}'+r'){\parbox[t]{'+str(w)+r'mm}{'+al+font+r'\fontsize{'+str(size)+'}{'+str(leading)+r'}\selectfont '+val+'}};')
 records.append(dict(page=page,x=x,y=y,w=w,size=size,leading=leading,text=s))
def rect(x,y,w,h,c,r=0):T.append(r'\fill['+c+(f',rounded corners={r}mm' if r else '')+'] '+f'({x},{y}) rectangle ({x+w},{y+h});')
def line(x1,y1,x2,y2,c='rule',lw=.6,dashed=False):T.append(r'\draw['+c+f',line width={lw}pt'+(',dashed' if dashed else '')+'] '+f'({x1},{y1}) -- ({x2},{y2});')
def poly(points,c='teal',lw=1.6):T.append(r'\draw['+c+f',line width={lw}pt,line join=round] '+' -- '.join(f'({x},{y})' for x,y in points)+';')
def dot(x,y,r,c):T.append(r'\fill['+c+'] '+f'({x},{y}) circle ({r}mm);')
def ranknum(x,y,n):T.append(r'\node[anchor=center,inner sep=0,text=white,font=\bfseries\fontsize{8.2}{10}\selectfont] at ('+f'{x},{y}'+r'){'+str(n)+'};')
def num(n,x,y,r=3.6):dot(x,y,r,'teal');text(x-r,y-2.6,2*r,n,11.2,12,'white',True,align='center')
def tick(x,y,label,w=16):text(x-w/2,y,w,label,8.4,11.4,'muted',align='center')
def image(x,y,w,h,path):
 T.append(r'\node[anchor=north west,inner sep=0] at ('+f'{x},{y}'+r'){\includegraphics[width='+str(w)+r'mm,height='+str(h)+r'mm,keepaspectratio]{'+str(path)+'}};')
def logo(name,x,y,size=4.7):
 if name in L:image(x,y,size,size,R/'source/assets'/L[name])
def panel(it,x,y):
 rect(x,y,124.5,78,'pale',1.2);num(it['id'],x+7,y+7)
 text(x+13,y+3.1,107.5,it['chart_title'],13.3,18.3,'navy',True)
 text(x+5,y+14.5,115,it['scope'],9.2,13,'muted');line(x+5,y+22,x+119.5,y+22,'rule',.4)

def chart1(x,y):
 for i,r in enumerate(D['1']['rows']):
  xx=x+5+i*29;col=['blue','teal','purple','navy'][i]
  text(xx,y+25,27,r['name'],10.1,13.3,col,True,align='center')
  text(xx,y+30.5,27,f"{r['ratio']:.2f}倍",13.0,16,col,True,align='center')
  by=y+65;ph=22;sc=ph/r['ymax']
  line(xx+1,by,xx+26,by,'rule',.5)
  for j,v in enumerate(r['values']):
   bx=xx+2+j*8.2;hh=v*sc
   rect(bx,by-hh,5.4,hh,col+f'!{[27,53,100][j]}',.35)
   label=(f'{v:.2f}' if i==3 else f'{v:.1f}')
   text(bx-2,by-hh-4.1,9.4,label,7.9,10.3,col if j==2 else 'muted',j==2,align='center')
   tick(bx+2.7,by+1,['24','25','26'][j],8)
  if i<3:line(xx+28,y+27,xx+28,y+69,'rule',.35)
 text(x+5,y+73,115,'单位：十亿次；各组独立标尺。倍数为2026 / 2025。',8.2,11.1,'muted')

def chart2(x,y):
 image(x+4,y+31,62,25,R/'source/assets/asset-world.pdf')
 text(x+5,y+25,60,'全球代码供给分布',9,12,'blue',True)
 # The geographic sample counts remain separate from the platform totals.
 text(x+5,y+57,61,'模型／数据集 · 发布者样本',8.3,11,'muted')
 text(x+5,y+62,61,'美国 45,801／5,871',9.2,12,'navy')
 text(x+5,y+67,61,'中国 6,017／1,338',9.2,12,'teal',True)
 for i,r in enumerate(D['2']['rows']):
  xx=x+70;yy=y+26+i*15;co=r['color']
  rect(xx,yy,49,13.2,'white',.6);rect(xx,yy,1.1,13.2,co)
  text(xx+3,yy+1,15,r['name'],9.3,12,co,True)
  text(xx+16,yy+.7,30,r['value'],15,18,co,True,align='right')
  text(xx+3,yy+7.7,45,('约+' if i else '+')+str(r['growth'])+'% · '+r['window'],7.9,10.5,'muted')
 text(x+5,y+73,115,'底色为代码数量；右侧为平台总量。HF窗口含期后。',8.2,11.1,'muted')

def chart3(x,y):
 px=x+25;pw=69
 for v in [0,200,400]:
  xx=px+pw*v/500;line(xx,y+29,xx,y+64,'grid',.4);tick(xx,y+65,str(v),15)
 for i,r in enumerate(D['3']['rows']):
  yy=y+28+i*12.2;text(x+5,yy+3,20,r['name'],10.1,13,'navy',True)
  for j,v in enumerate(r['values']):
   v/=10000;by=yy+j*4.7
   rect(px,by,pw*v/500,3.4,'yearold' if j==0 else 'teal',.25)
   text(px+pw*v/500+1.1,by-.7,15,f'{v:.1f}',8.2,10.5,'muted' if j==0 else 'teal',j==1)
  text(x+101,yy+2,19,f"+{r['growth']:.1f}%",10.6,14,'teal',True,align='right')
 rect(x+5,y+67,2.5,2.5,'yearold');text(x+9,y+66.3,18,'2025',8.2,11,'muted')
 rect(x+27,y+67,2.5,2.5,'teal');text(x+31,y+66.3,18,'2026',8.2,11,'muted')
 text(x+92,y+66.3,28,'单位：万人',8.2,11,'muted',align='right')
 text(x+5,y+73,115,'六国：巴西、印尼、越南、埃及、菲律宾、南非。',8.2,11.1,'muted')

def chart4(x,y):
 px=x+15;py=y+65;pw=70;ph=30
 for v in [0,200,400]:
  yy=py-v/500*ph;line(px,yy,x+89,yy,'grid',.4)
  text(x+3,yy-2,10,str(v),8.2,11,'muted',align='right')
 for k,r in enumerate(D['4']['rows']):
  co='teal' if k==0 else 'blue';pts=[(px+j*pw/4,py-(v/10000)/500*ph) for j,v in enumerate(r['values'])]
  poly(pts,co,2.0)
  for xx,yy in pts:dot(xx,yy,1.15,co)
  end=pts[-1]
  text(x+91,y+33+k*14,29,r['name'],9.5,12.5,co,True)
  text(x+91,y+38+k*14,29,f"{r['values'][-1]/10000:.1f}",16.0,19,co,True)
 for j,yr in enumerate(D['4']['years']):tick(px+j*pw/4,y+67,str(yr)[2:],13)
 text(x+5,y+25,115,'中国同比 +47.2% · 美国 +8.9%',10.7,14,'teal',True)
 text(x+91,y+62,30,'万OpenRank',8.2,11,'muted')
 text(x+5,y+73,115,'独立地区比较口径；不与第19页下方自然年序列混用。',8.1,11.1,'muted')

def chart5(x,y):
 px=x+23;pw=62;top=y+27
 for i,r in enumerate(D['5']['rows']):
  yy=top+i*7.3;v=r['downloads']/1e8;co='teal' if i==0 else 'blue!60'
  text(x+5,yy+.1,16,str(i+1)+' '+r['name'],9.7,13,'teal' if i==0 else 'navy',i==0)
  rect(px,yy+1,pw*v/35,4.3,co,.3)
  text(px+pw*v/35+1.5,yy+.2,18,f'{v:.2f}',9.6,13,'teal' if i==0 else 'muted',i==0)
 text(x+101,y+28,18,'#1',23,27,'teal',True,align='center')
 text(x+99.5,y+39,23,r'五城模型\\下载排名',9.0,12,'muted',align='center',raw=True)
 text(x+98,y+54,22,'16.02万',12.6,16,'purple',True,align='center')
 text(x+97,y+61,24,'直接衍生模型',8.1,11,'muted',align='center')
 text(x+5,y+66,90,'模型累计下载 · 单位：亿次',8.5,11.5,'muted')
 text(x+5,y+73,115,'五城样本排名；下载不等于用户，衍生为直接关联。',8.2,11.1,'muted')

def rankline(xs,ys,color):poly(list(zip(xs,ys)),color,2);[dot(a,b,1.5,color) for a,b in zip(xs,ys)]
def chart6(x,y):
 # Adjacent-month crossover, followed by an explicitly separate June check.
 xx=[x+18,x+62,x+100]
 text(x+5,y+25,115,'2月 → 3月：头部交叉；6月仍居首',10.3,13.8,'teal',True)
 for i,lab in enumerate(['2026.02','2026.03','2026.06']):tick(xx[i],y+30,lab,26)
 for rank in [1,2,3]:line(x+13,y+39+(rank-1)*10,x+110,y+39+(rank-1)*10,'grid',.4)
 for i,r in enumerate(D['6']['rows']):
  co=['teal','blue','yearold'][i];ys=[y+39+(v-1)*10 for v in r['ranks']]
  # Feb-March is an adjacent comparison; March-June is a selected-endpoint segment.
  rankline(xx,ys,co)
  for j,v in enumerate(r['ranks']):ranknum(xx[j],ys[j],v)
  logo(r['name'],x+112,ys[-1]-2,4.2);text(x+117,ys[-1]-1.6,8,r['name'],8.0,11,'navy')
 text(x+5,y+66,115,'3月：华为12,344.42  ＞  微软11,759.49',9.4,12.6,'navy',True)
 text(x+5,y+73,115,'主期全年榜仍为微软第1、华为第2；上图为月榜选点。',8.0,11.1,'muted')

def chart7(x,y):
 xx=[x+20,x+58,x+95]
 for i,lab in enumerate(['2025.05','2025.06','2025.07']):tick(xx[i],y+25,lab,27)
 # rank diagram makes the family-aggregation convention explicit.
 for rank in [1,2,3]:line(x+15,y+36+(rank-1)*10,x+105,y+36+(rank-1)*10,'grid',.4)
 names=['Linux 基金会及子基金会','开放原子开源基金会','Apache 软件基金会']
 for i,r in enumerate(D['7']['rows']):
  co=['blue','teal','purple'][i];ys=[y+36+(v-1)*10 for v in r['ranks']];rankline(xx,ys,co)
  for j,v in enumerate(r['ranks']):ranknum(xx[j],ys[j],v)
  logo(names[i],x+105,ys[-1]-2.1,4.4);text(x+111,ys[-1]-1.8,14,['LF族','开放原子','Apache'][i],8,10.5,co,True)
 text(x+5,y+63,115,'6月：开放原子9,313.85  ＞  Apache 9,105.36',9.3,12.5,'navy',True)
 text(x+5,y+68,115,'LF族当月21,744.37 · 14个标签汇总，非仓库去重值',8.2,11,'muted')
 text(x+5,y+73,115,'历史事件，早于主期；当前标签回溯，非治理质量排行。',8.0,11.1,'muted')

def chart8(x,y):
 text(x+5,y+24.5,115,'86项目 / 12类   ·   48个仓库创建于2025年以来',9.5,13,'navy',True)
 groups=[('application','任务入口','purple'),('framework','构建与编排','teal'),('runtime','运行支撑','blue')]
 for gi,(key,label,co) in enumerate(groups):
  xx=x+5+gi*39;cw=36.5;items=[c for c in D['8']['categories'] if c['group']==key]
  rect(xx,y+31,cw,5,co,.4);text(xx,y+31.6,cw,label,8.7,11,'white',True,align='center')
  rh=6.9 if len(items)==5 else 8.5
  for k,r in enumerate(items):
   yy=y+37+k*rh
   rect(xx,yy,cw,rh-.7,'white',.3)
   text(xx+1.2,yy+.2,cw-3,r['name']+' '+str(r['total']),8.2,10.8,co,True)
   logo(r['example'],xx+1.2,yy+3.4,2.6)
   text(xx+4.8,yy+3.5,cw-6,r['example'],7.3,9.3,'muted')
  if key=='framework':
   text(xx,y+64,cw,'55.8%',17.3,21,'teal',True,align='center')
 text(x+5,y+73,115,'每类选列1项；完整名单见4.1。55.8%为创建比例。',8.0,11.1,'muted')

charts=[chart1,chart2,chart3,chart4,chart5,chart6,chart7,chart8]
for p,pg in enumerate(C['pages'],1):
 page=p
 if p>1:T.append(r'\newpage')
 T.append(r'\null\begin{tikzpicture}[remember picture,overlay,x=1mm,y=-1mm]\begin{scope}[shift={(current page.north west)}]')
 text(20,29,257,'年度变化专题 / '+('01—04' if p==1 else '05—08'),10.4,15,'teal',True)
 text(20,40,257,C['title'],28,35,'navy',True,True)
 text(20,55,257,pg['subtitle'],17,24,'teal',True)
 text(20,68,257,pg['lead'],12.5,19)
 for j,it in enumerate(pg['items']):
  x=20+(j%2)*132.5;y=88+(j//2)*86;panel(it,x,y);charts[it['id']-1](x,y)
 if p==1:
  foot=r'① \href{'+GH+r'}{GitHub Octoverse 2026}：各年截至9月30日的12个月，含公开和私有仓库。②本报告图2-13与\href{'+HF+r'}{HF夏季报告}：代码同比、模型与数据年内增长分别标注。③④本报告2.1—2.2地区表，报告年度为7月至次年6月；不与GitHub单平台国家榜混算。'
 else:
  foot='⑤《杭州市开源生态全景报告》2026年7月，第3、20页；HF五城机构样本，期后快照。⑥⑦OpenShare原始月榜2026.02、03、06及2025.05—07；LF族汇总遵循本报告，标签可重叠。⑧4.1固定清单e330d75，按仓库创建时间核算；不据此推算2025版名单更替率。'
 foot+=' 完整口径见附录第116页。'
 text(20,256,257,foot,9.1,13.3,'muted',raw=(p==1))
 line(20,272,277,272);text(20,277,257,'变化意味着什么',11.4,16,'teal',True)
 for j,it in enumerate(pg['items']):
  x=20+(j%2)*132.5;y=285+(j//2)*53
  num(it['id'],x+3.6,y+3.7);text(x+10,y,114.5,it['title'],14.0,19.0,'navy',True)
  text(x,y+10,124.5,it['body'],13.6,19.2)
 T.append(r'\end{scope}\end{tikzpicture}')
colors={'navy':'112C53','body':'24364C','muted':'526B80','teal':'007E86','purple':'7853AD','blue':'386C9E','rust':'AD6574','yearold':'9FAFBE','track':'DDE6ED','rule':'CFDCE5','grid':'DCE5EB','pale':'F4F7FA','postshade':'E2E8EE','white':'FFFFFF','spec1':'5897EC','spec2':'68CBE0','spec3':'6CBCA7','spec4':'8ABF75','spec5':'B6CB46','spec6':'F3D540','spec7':'EEA54A','spec8':'DE6A87','spec9':'B664BD','spec10':'8C5CD0'}
preamble=r'''\documentclass{article}
\usepackage[paperwidth=297mm,paperheight=420mm,margin=0mm]{geometry}
\usepackage{fontspec}
\usepackage{tikz}
\usepackage{graphicx}
\usepackage{hyperref}
\setmainfont{NotoSansCJK-Regular.ttc}[Path=/usr/share/fonts/opentype/noto/,FontIndex=2,BoldFont=NotoSansCJK-Bold.ttc,BoldFeatures={FontIndex=2}]
\newfontfamily\serif{NotoSerifCJK-Regular.ttc}[Path=/usr/share/fonts/opentype/noto/,FontIndex=2,BoldFont=NotoSerifCJK-Bold.ttc,BoldFeatures={FontIndex=2}]
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip=0pt plus 1pt
\pagestyle{empty}\setlength{\parindent}{0pt}
\hypersetup{pdftitle={2025—2026：全球开源的八大变化},pdfauthor={GOSD Editorial Team},pdfsubject={中文年度变化专题 v0.5；COSSI全文v1.7整合},hidelinks}
'''
preamble+='\n'.join(r'\definecolor{'+k+'}{HTML}{'+v+'}' for k,v in colors.items())
(R/'source/annual_change_insert.tex').write_text(preamble+'\n\\begin{document}\n'+'\n'.join(T)+'\n\\end{document}\n')
(R/'qa/layout.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('Generated two-page Chinese 4+4 layout v0.5.')
