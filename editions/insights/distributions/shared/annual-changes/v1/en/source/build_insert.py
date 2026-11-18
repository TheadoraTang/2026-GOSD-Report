"""Build the two-page English review insert; no full-report mutation.

All plotted numbers are read unchanged from the approved Chinese v0.5 data.
English units and typography are adapted explicitly. Compile generated TeX
twice with XeLaTeX. See README.md for a portable build command.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'source'
C = json.loads((SRC / 'content-en.json').read_text())
D = json.loads((SRC / 'approved-zh-chart-data.json').read_text())
L = {r['name']: r['file'] for r in json.loads((SRC/'assets/logos.json').read_text())}
for folder in ('qa', 'output'):
    (ROOT/folder).mkdir(exist_ok=True)
T, RECORDS = [], []
PAGE = 0
GH = 'https://github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents/'
HF = 'https://huggingface.co/blog/state-of-open-models-summer-2026'
COMPANY = 'https://open-share.com/insight/open-leaderboard?scope=Global&unit=Initiator&timeType=month&time=2026-03&search=&page=1'
FOUNDATION = 'https://open-share.com/insight/open-leaderboard?scope=Global&unit=Foundation&timeType=month&time=2025-06&search=&page=1'
LANDSCAPE = 'https://github.com/X-lab2017/2026-Global-Open-Source-Development-Report/blob/c51e3441361407b68f10b339d97eff288319b503/preview/content/landscape/data/agentic-ai-projects.csv'

def esc(s):
    return str(s).replace('&', r'\&').replace('%', r'\%').replace('_', r'\_').replace('#', r'\#')

def text(x, y, w, s, size=12, leading=16.5, color='body', bold=False,
         serif=False, align='left', raw=False, role='text'):
    val = s if raw else esc(s)
    font = ('\\serif ' if serif else '') + ('\\bfseries ' if bold else '')
    al = {'left': r'\raggedright ', 'center': r'\centering ', 'right': r'\raggedleft '}[align]
    T.append(r'\node[anchor=north west,inner sep=0,text='+color+'] at ('+f'{x},{y}'+r'){\parbox[t]{'+str(w)+r'mm}{'+al+font+r'\fontsize{'+str(size)+'}{'+str(leading)+r'}\selectfont '+val+'}};')
    RECORDS.append(dict(page=PAGE,x=x,y=y,w=w,size=size,leading=leading,text=s,role=role))

def rect(x,y,w,h,c,r=0):
    T.append(r'\fill['+c+(f',rounded corners={r}mm' if r else '')+'] '+f'({x},{y}) rectangle ({x+w},{y+h});')

def line(x1,y1,x2,y2,c='rule',lw=.55,dashed=False):
    T.append(r'\draw['+c+f',line width={lw}pt'+(',dashed' if dashed else '')+'] '+f'({x1},{y1}) -- ({x2},{y2});')

def poly(points,c='teal',lw=1.6,dashed=False):
    T.append(r'\draw['+c+f',line width={lw}pt,line join=round'+(',dashed' if dashed else '')+'] '+' -- '.join(f'({x},{y})' for x,y in points)+';')

def dot(x,y,r,c):
    T.append(r'\fill['+c+'] '+f'({x},{y}) circle ({r}mm);')

def centered(x,y,s,size=9,color='white',bold=True):
    T.append(r'\node[anchor=center,inner sep=0,text='+color+r',font='+('\\bfseries' if bold else '')+r'\fontsize{'+str(size)+'}{'+str(size*1.2)+r'}\selectfont] at ('+f'{x},{y}'+r'){'+esc(s)+'};')

def num(n,x,y,r=3.35):
    dot(x,y,r,'teal'); centered(x,y,n,11.1)

def tick(x,y,label,w=16,size=8.8):
    text(x-w/2,y,w,label,size,size*1.25,'muted',align='center')

def image(x,y,w,h,path):
    # Relative paths make the exported source bundle portable.
    relative = str(path.relative_to(SRC))
    T.append(r'\node[anchor=north west,inner sep=0] at ('+f'{x},{y}'+r'){\includegraphics[width='+str(w)+r'mm,height='+str(h)+r'mm,keepaspectratio]{'+relative+'}};')

def logo(name,x,y,size=4):
    if name in L:
        image(x,y,size,size,SRC/'assets'/L[name])

def page_frame(p):
    # The narrow bottom ribbon is taken from the approved English background.
    # Other image areas are masked so all reading surfaces remain white.
    image(0,0,297,420,SRC/'assets/english-page-background.png')
    rect(0,0,297,390,'white'); rect(0,392.4,297,27.6,'white')
    text(23.5,12.6,31,'GOSD',17,20,'navy',True,True)
    text(57.4,13.2,180,'2026 Global Open Source Development Report',10.6,14,'muted')
    text(228,13.2,45.5,'ESSENTIAL EDITION',9.2,12,'muted',align='right')
    line(23.5,25.5,273.5,25.5)
    for i in range(10): rect(193.5+i*8.05,25.05,6.8,.8,'spec'+str(i+1))
    line(17.6,406,279.4,406)
    text(17.6,410.4,230,'GOSD 2026 · COSSI EDITION · ENGLISH',9,12,'muted')
    text(261.5,410.1,17.9,f'{p:02}',10,13,'muted',True,align='right')

def panel(it,x,y):
    rect(x,y,121,78,'pale',1.1)
    num(it['id'],x+6.8,y+6.5)
    text(x+12.5,y+3.4,104,it['chart_title'],12.4,15.7,'navy',True,role='panel-title')
    text(x+4.5,y+14.5,112,it['scope'],9.15,12.1,'muted',role='panel-scope')
    line(x+4.5,y+22,x+116.5,y+22,'rule',.45)

def chart1(x,y):
    for i,r in enumerate(D['1']['rows']):
        xx=x+4.3+i*28.0; co=['blue','teal','purple','navy'][i]
        text(xx,y+25,26.6,['Pushes','Commits','Actions jobs','Merged PRs'][i],9.4,12,co,True,align='center')
        text(xx,y+31,26.6,f"{r['ratio']:.2f}×",14.2,17,co,True,align='center')
        by=y+64.4; sc=22/r['ymax']
        line(xx+1,by,xx+25.4,by,'rule',.45)
        for j,v in enumerate(r['values']):
            bx=xx+1.6+j*8.2; hh=v*sc
            rect(bx,by-hh,5.4,hh,co+f'!{[25,52,100][j]}',.3)
            label=(f'{v:.3f}' if i==3 else f'{v:.1f}')
            text(bx-2.2,by-hh-4.2,9.8,label,8.15,10.5,co if j==2 else 'muted',j==2,align='center')
            tick(bx+2.7,by+1.2,str(D['1']['years'][j]),9,7.8)
        if i<3:line(xx+27.2,y+26,xx+27.2,y+69,'rule',.35)
    text(x+4.5,y+72.9,112,'Billions · independent scales · multiples are 2026 / 2025',8.65,11.3,'muted')

def chart2(x,y):
    text(x+4.5,y+25,58,'Public code repository distribution',9.1,12,'blue',True)
    image(x+4.5,y+31,56,23.5,SRC/'assets/asset-world.pdf')
    for i in range(6):rect(x+5+i*4.2,y+53.8,4,1.45,f'blue!{20+i*15}')
    text(x+32,y+52.7,29,'Fewer to more',7.9,10,'muted')
    text(x+4.5,y+57.8,59,'Geolocated publisher sample',8.7,11.3,'muted')
    text(x+4.5,y+62.1,59,'Models / datasets',8.4,10.8,'muted')
    text(x+4.5,y+66.2,60,'US 45,801 / 5,871',9.15,11.7,'navy')
    text(x+4.5,y+70.4,60,'China 6,017 / 1,338',9.15,11.7,'teal',True)
    rows=[('Public repos','454M','+22.3%','Q2 2025–Q2 2026','blue'),
          ('Models','2.96M','About +21.8%','Jan–Aug 2026','purple'),
          ('Datasets','1.00M','About +40.6%','Jan–Aug 2026','teal')]
    for i,(lab,val,grow,window,co) in enumerate(rows):
        xx=x+65.0; yy=y+25+i*15.65
        rect(xx,yy,51.5,14.0,'white',.6);rect(xx,yy,1.05,14.0,co)
        text(xx+2.5,yy+1.1,25,lab,8.9,11.3,co,True)
        text(xx+25,yy+.2,24,val,14,17,co,True,align='right')
        text(xx+2.5,yy+6.3,46,grow+' · '+window,8.2,10.4,'muted')
    text(x+65,y+73,51.5,'HF includes post-period data.',7.9,10.1,'muted')

def chart3(x,y):
    px=x+28;pw=63
    for v in [0,2,4]:
        xx=px+pw*v/5;line(xx,y+27,xx,y+63,'grid',.4);tick(xx,y+64,str(v),10,8.2)
    for i,r in enumerate(D['3']['rows']):
        yy=y+29+i*12.2
        name=['China','India','Six countries'][i]
        text(x+4.5,yy+2.1,23,name,9.4,12.1,'navy',True)
        for j,v in enumerate(r['values']):
            value=v/1e6; by=yy+j*4.7
            rect(px,by,pw*value/5,3.25,'yearold' if j==0 else 'teal',.25)
            text(px+pw*value/5+1.1,by-.6,15,f'{value:.2f}',8.6,11,'muted' if j==0 else 'teal',j==1)
        text(x+98,yy+1.7,18.5,f"+{r['growth']:.1f}%",10.1,13,'teal',True,align='right')
    rect(x+4.5,y+25,2.3,2.3,'yearold');text(x+8.2,y+24.2,17,'2025',8.6,11,'muted')
    rect(x+24,y+25,2.3,2.3,'teal');text(x+27.7,y+24.2,17,'2026',8.6,11,'muted')
    text(x+91,y+64.2,25.5,'Millions',8.6,11,'muted',align='right')
    text(x+4.5,y+69.6,112,'Six countries: Brazil, Indonesia, Vietnam, Egypt, Philippines and South Africa.',8.6,11.1,'muted')

def chart4(x,y):
    px=x+14;py=y+64;pw=65;ph=30
    text(x+4.5,y+25,112,'Year-on-year: China +47.2% · US +8.9%',10.1,13,'teal',True)
    for v in [0,2,4]:
        yy=py-v/5*ph;line(px,yy,x+83,yy,'grid',.4)
        text(x+3,yy-2.1,8,str(v),8.7,11,'muted',align='right')
    for k,r in enumerate(D['4']['rows']):
        co='teal' if k==0 else 'blue'
        pts=[(px+j*pw/4,py-v/1e6/5*ph) for j,v in enumerate(r['values'])]
        poly(pts,co,1.9)
        for xx,yy in pts:dot(xx,yy,1.12,co)
        text(x+87,y+34+k*13.8,29,['China','United States'][k],9.3,12,co,True)
        text(x+87,y+38.8+k*13.8,29,f"{r['values'][-1]/1e6:.3f}M",14.6,17.6,co,True)
    for j,yr in enumerate(D['4']['years']):tick(px+j*pw/4,y+66,str(yr),14,8.2)
    text(x+86,y+63,30,'OpenRank',8.5,10.9,'muted')
    text(x+4.5,y+72.8,112,'Millions · distinct from calendar-year and GitHub-only series',8.55,11.1,'muted')

def chart5(x,y):
    px=x+28;pw=54
    for i,r in enumerate(D['5']['rows']):
        yy=y+27+i*7.35;v=r['downloads']/1e9;co='teal' if i==0 else 'blue!60'
        text(x+4.5,yy+.1,23,['Hangzhou','Beijing','Shanghai','Hefei','Shenzhen'][i],9.45,12.2,'teal' if i==0 else 'navy',i==0)
        rect(px,yy+1,pw*v/3.5,4.2,co,.3)
        text(px+pw*v/3.5+1.1,yy+.1,16,f'{v:.3f}',9.15,12,'teal' if i==0 else 'muted',i==0)
    text(x+98,y+27,19,'#1',22,26,'teal',True,align='center')
    text(x+97,y+37.7,20,'of five cities',8.5,11,'muted',align='center')
    text(x+95.8,y+52,22.4,'160.2k',12.5,15.5,'purple',True,align='center')
    text(x+96,y+58.3,22,'direct derivatives',8.5,10.8,'muted',align='center')
    text(x+4.5,y+66.4,112,'Cumulative model downloads · billions',9.0,11.5,'muted')
    text(x+4.5,y+72.8,112,'Five-city sample; downloads are not unique users.',8.65,11.2,'muted')

def bump(xs,ys,co,selected=False):
    if selected:
        poly(list(zip(xs[:2],ys[:2])),co,1.9)
        poly(list(zip(xs[1:],ys[1:])),co,1.9,dashed=True)
    else:poly(list(zip(xs,ys)),co,1.9)
    for xx,yy in zip(xs,ys):dot(xx,yy,1.95,co)

def chart6(x,y):
    xs=[x+17,x+47,x+78]
    for i,lab in enumerate(['Feb 2026','Mar 2026','Jun 2026']):tick(xs[i],y+26,lab,25,9)
    for rank in [1,2,3]:line(x+12,y+36+(rank-1)*10.3,x+81,y+36+(rank-1)*10.3,'grid',.4)
    for i,r in enumerate(D['6']['rows']):
        co=['teal','blue','yearold'][i];ys=[y+36+(v-1)*10.3 for v in r['ranks']]
        bump(xs,ys,co,True)
        for j,v in enumerate(r['ranks']):centered(xs[j],ys[j],v,8.3)
        logo(r['name'],x+84,ys[-1]-1.8,3.5)
        text(x+89.2,ys[-1]-1.8,28,['Huawei','Microsoft','Google'][i],9.5,12.1,co if i<2 else 'muted',i<2)
    text(x+4.5,y+64.4,112,'March: Huawei 12,344.42 > Microsoft 11,759.49',9.45,12.1,'navy',True)
    text(x+4.5,y+71.7,112,'Full main period: Microsoft #1; Huawei #2.',9.0,11.6,'muted')

def chart7(x,y):
    xs=[x+17,x+47,x+77]
    for i,lab in enumerate(['May 2025','Jun 2025','Jul 2025']):tick(xs[i],y+25,lab,25,9)
    for rank in [1,2,3]:line(x+12,y+35+(rank-1)*10.0,x+80,y+35+(rank-1)*10.0,'grid',.4)
    original=['Linux 基金会及子基金会','开放原子开源基金会','Apache 软件基金会']
    for i,r in enumerate(D['7']['rows']):
        co=['blue','teal','purple'][i];ys=[y+35+(v-1)*10 for v in r['ranks']]
        bump(xs,ys,co)
        for j,v in enumerate(r['ranks']):centered(xs[j],ys[j],v,8.3)
        logo(original[i],x+83.5,ys[-1]-1.75,4.1)
        text(x+89.2,ys[-1]-1.8,27,['LF family','OpenAtom','Apache'][i],9.35,12,co,True)
    text(x+4.5,y+62.6,112,'June: OpenAtom 9,313.85 > Apache 9,105.36',9.4,12.1,'navy',True)
    text(x+4.5,y+68.2,112,'LF family: 21,744.37 · 14 tags; not deduplicated',8.55,11.1,'muted')
    text(x+4.5,y+73.2,112,'Historical crossover: June 2025 precedes the main period.',8.4,10.9,'muted')

def chart8(x,y):
    text(x+4.5,y+24.6,112,'86 projects / 12 categories · 48 repos created since Jan 2025',9.6,12.4,'navy',True)
    short=['Coding agents','Coding workflows','Personal assistants','Chat workspaces','Multi-agent','Agent builders','Code frameworks','Memory & context','Protocols','Tools / web / UI','Sandboxes','Observability / eval.']
    names={r['id']:short[i] for i,r in enumerate(D['8']['categories'])}
    groups=[('application','Applications','purple'),('framework','Build & orchestrate','teal'),('runtime','Runtime services','blue')]
    for gi,(key,label,co) in enumerate(groups):
        xx=x+4.5+gi*38.2;cw=35.6
        items=[c for c in D['8']['categories'] if c['group']==key]
        rect(xx,y+31,cw,5,co,.4)
        text(xx,y+31.75,cw,label,8.85,11.5,'white',True,align='center')
        rh=7.25
        for k,r in enumerate(items):
            yy=y+37+k*rh
            rect(xx,yy,cw,rh-.55,'white',.3)
            text(xx+1.1,yy+.25,cw-5.4,names[r['id']],8.45,10.6,co,True)
            text(xx+cw-4.8,yy+.25,3.7,str(r['total']),8.45,10.6,co,True,align='right')
            logo(r['example'],xx+1.1,yy+3.6,2.5)
            text(xx+4.6,yy+3.25,cw-5.6,r['example'],8.6,10.6,'muted')
        if key=='framework':
            text(xx,y+61.3,cw,'55.8%',18,21.5,'teal',True,align='center')
            text(xx,y+69.6,cw,'Creation share',8.2,10.5,'muted',align='center')
    text(x+4.5,y+74.3,112,'One example per category · creation share is not turnover.',8.35,10.8,'muted')

charts=[chart1,chart2,chart3,chart4,chart5,chart6,chart7,chart8]
for p,pg in enumerate(C['pages'],1):
    PAGE=p
    if p>1:T.append(r'\newpage')
    T.append(r'\null\begin{tikzpicture}[remember picture,overlay,x=1mm,y=-1mm]\begin{scope}[shift={(current page.north west)}]')
    page_frame(p)
    text(23.5,32,250,'2025–2026 / ANNUAL CHANGES · '+('01–04' if p==1 else '05–08'),10.4,14,'teal',True)
    text(23.5,40.5,250,C['title'],33.2,39,'navy',True,True)
    text(23.5,55.0,250,pg['subtitle'],18.8,23.8,'navy',True,True)
    text(23.5,66,250,pg['lead'],12.3,17.1,'body')
    for j,it in enumerate(pg['items']):
        x=23.5+(j%2)*129;y=80+(j//2)*84
        panel(it,x,y);charts[it['id']-1](x,y)
    if p==1:
        foot=(r'\textbf{Sources and scope.} [1] \href{'+GH+r'}{GitHub Octoverse 2026}: public and private repositories; external reporting years ending 30 September. '
              r'[2] GOSD §2.5 and \href{'+HF+r'}{Hugging Face, State of Open Models: Summer 2026}: code, Q2 2025–Q2 2026; models and datasets, January–August 2026, including post-period data. HF growth rates use rounded totals. '
              r'[3–4] GOSD §§2.1–2.2: compiled regional series; report years run July–June. The six-country group excludes China and India and does not represent the whole Global South. '
              r'\textbf{Main reporting period: 1 July 2025–30 June 2026.}')
    else:
        foot=(r'\textbf{Sources and scope.} [5] Hangzhou Open Source Ecosystem Panorama Report, July 2026, pp. 3, 20; five-city institutional publishers, snapshot 17 July. '
              r'[6–7] \href{'+COMPANY+r'}{OpenShare enterprise} and \href{'+FOUNDATION+r'}{foundation monthly boards}; GOSD §§3.2–3.3. LF family means Linux Foundation plus sub-foundations: 14 current tags backcast over time, with possible overlap; not a governance-quality ranking. '
              r'[8] GOSD §4.1, \href{'+LANDSCAPE+r'}{pinned landscape e330d75}, 27 September 2026; 48/86 = 55.8\% is a repository-creation share, not replacement of the 2025 report’s project list. '
              r'\textbf{Historical events and post-period snapshots are labelled separately.}')
    text(23.5,245.6,250,foot,9.05,12.3,'muted',raw=True,role='source-notes')
    line(23.5,271.4,273.5,271.4)
    text(23.5,274.3,250,'WHAT THE CHANGES MEAN',10.5,14,'teal',True)
    for j,it in enumerate(pg['items']):
        x=23.5+(j%2)*129;y=284+(j//2)*51.5
        num(it['id'],x+3.35,y+3.2)
        text(x+9,y+.1,112,it['title'],12.65,16.1,'navy',True,role='analysis-title')
        text(x,y+10.1,121,it['body'],11.8,16.5,'body',role='analysis-body')
    T.append(r'\end{scope}\end{tikzpicture}')

colors={'navy':'112C53','body':'24364C','muted':'526B80','teal':'007E86','purple':'7853AD','blue':'386C9E','yearold':'9FAFBE','rule':'CFDCE5','grid':'DCE5EB','pale':'F4F7FA','white':'FFFFFF','spec1':'5897EC','spec2':'68CBE0','spec3':'6CBCA7','spec4':'8ABF75','spec5':'B6CB46','spec6':'F3D540','spec7':'EEA54A','spec8':'DE6A87','spec9':'B664BD','spec10':'8C5CD0'}
preamble=r'''\documentclass{article}
\usepackage[paperwidth=297mm,paperheight=420mm,margin=0mm]{geometry}
\usepackage{fontspec}
\usepackage{tikz}
\usepackage{graphicx}
\usepackage{hyperref}
\setmainfont{NotoSans-Regular.ttf}[Path=/usr/share/fonts/truetype/noto/,BoldFont=NotoSans-Bold.ttf]
\newfontfamily\serif{LiberationSerif-Regular.ttf}[Path=/usr/share/fonts/truetype/liberation/,BoldFont=LiberationSerif-Bold.ttf]
\pagestyle{empty}\setlength{\parindent}{0pt}
\hyphenpenalty=10000\exhyphenpenalty=10000
\hypersetup{pdftitle={2025–2026: Eight Shifts in Global Open Source},pdfauthor={GOSD Editorial Team},pdfsubject={COSSI English review insert v0.1; two A3 portrait pages; not merged into the full report},hidelinks}
'''
preamble+='\n'.join(r'\definecolor{'+k+'}{HTML}{'+v+'}' for k,v in colors.items())
(SRC/'annual_changes_en.tex').write_text(preamble+'\n\\begin{document}\n'+'\n'.join(T)+'\n\\end{document}\n')
(ROOT/'qa/layout.json').write_text(json.dumps(RECORDS,ensure_ascii=False,indent=2))
print('Generated English review insert v0.1: two native A3 pages.')
