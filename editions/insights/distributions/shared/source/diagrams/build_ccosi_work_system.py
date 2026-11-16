from pathlib import Path
import json,html
P=Path(__file__).resolve().parent
NAVY='#102B50'; TEAL='#007F85'; PALE='#F1F7F9'; PALE2='#E6F2F3'; RULE='#BEDCDF'; MUTED='#47717D'; WHITE='#FFFFFF'
elems=[]
def rect(id,x,y,w,h,fill,stroke=None,sw=.6):
 d={'id':id,'type':'rect','x':x,'y':y,'w':w,'h':h,'fill':fill}
 if stroke:d.update(stroke=stroke,stroke_width=sw)
 elems.append(d)
def line(id,x1,y1,x2,y2,color=RULE,sw=.55):elems.append({'id':id,'type':'line','x1':x1,'y1':y1,'x2':x2,'y2':y2,'color':color,'stroke_width':sw})
def poly(id,points,fill):elems.append({'id':id,'type':'polygon','points':points,'fill':fill})
def text(id,s,x,y,size=8.4,color=NAVY,weight=400,anchor='middle'):
 elems.append({'id':id,'type':'text','text':s,'x':x,'y':y,'size':size,'font_family':'Noto Sans CJK SC','weight':weight,'color':color,'anchor':anchor,'baseline':'alphabetic'})
rect('canvas',0,0,493,300,WHITE)
rect('practice_header',0,0,330,19,TEAL)
text('practice_title','实践与传播',165,13.1,10.4,WHITE,700)
for i,s in enumerate(['智库报告','学术大会','开源案例','开源科普','开源大赛']):
 x=i*66.6
 rect(f'practice_cell_{i}',x,22,63.6,23,PALE2)
 text(f'practice_item_{i}',s,x+31.8,37,8.8,TEAL,500)
for i,x in enumerate([15,308]):
 rect(f'up_arrow_stem_{i}',x+4.5,56,6,7.5,'#6EB8BA')
 poly(f'up_arrow_head_{i}',[[x,56],[x+15,56],[x+7.5,49]],'#6EB8BA')
text('technical_support','技术支撑',82,59.5,8.6,NAVY,500)
text('governance_guidance','治理引导',248,59.5,8.6,NAVY,500)
for x,title,key in [(0,'开源创新组件','innovation'),(168,'开源治理要素','governance')]:
 rect(key+'_header',x,69,162,21,TEAL)
 text(key+'_title',title,x+81,83.2,10,WHITE,700)
 rect(key+'_body',x,94,162,202,PALE)
 line(key+'_rule_1',x+9,158,x+153,158)
 line(key+'_rule_2',x+9,223,x+153,223)
left_groups=[
 ('software','开源软件',108,[('代码开源',42,126),('文档开源',122,126),('开放过程',42,144),('开放治理',122,144)]),
 ('ai','开源 AI',173,[('权重开放',42,191),('架构开放',122,191),('工具开源',42,209),('数据开放',122,209)]),
 ('hardware','开源硬件',238,[('设计开源',42,256),('制造开放',122,256),('协议开源',42,274),('接口开放',122,274)])]
for key,title,yy,items in left_groups:
 text(key+'_heading',title,81,yy,9.6,NAVY,700)
 for j,(s,x,y) in enumerate(items):text(key+f'_item_{j}',s,x,y,8.6)
mid_groups=[
 ('policy','政策治理',108,[('开源合规',210,126),('开源回馈',290,126),('知识产权',210,144),('数字主权',290,144)]),
 ('technology','技术治理',173,[('基础软件',210,191),('云计算',290,191),('大数据',210,209),('人工智能',290,209)]),
 ('standards','标准治理',238,[('要素标准',210,256),('流程标准',290,256),('开源文化培育',249,277)])]
for key,title,yy,items in mid_groups:
 text(key+'_heading',title,249,yy,9.6,NAVY,700)
 for j,(s,x,y) in enumerate(items):text(key+f'_item_{j}',s,x,y,8.6)
rect('evaluation_header',343,0,150,19,NAVY)
text('evaluation_title','开源发展评价',418,13.1,10.4,WHITE,700)
for key,y,h,title,ty in [('sustainability',22,73,'可持续发展',37),('subjects',101,53,'评价主体',116),('indicators',160,62,'评价指标',175),('infrastructure',228,68,'评价设施',243)]:
 rect(key+'_panel',343,y,150,h,PALE2 if key=='sustainability' else PALE)
 text(key+'_heading',title,418,ty,9.6,NAVY,700)
for i,(s,x,y) in enumerate([('资金支持稳定性',380,55),('政策支持一致性',456,55),('资源分配合理性',380,76),('人才培养系统性',456,76)]):text(f'sustainability_item_{i}',s,x,y,8.2)
for i,(s,x) in enumerate([('项目',368),('企业',418),('开发者',468)]):text(f'subject_item_{i}',s,x,139,8.6)
for i,(s,x,y) in enumerate([('活跃度',380,193),('贡献度',456,193),('影响力',380,211),('成本效益',456,211)]):text(f'indicator_item_{i}',s,x,y,8.6)
for i,(s,x,y) in enumerate([('专家智库',380,261),('数据',456,261),('方法流程',380,279),('工具',456,279)]):text(f'infrastructure_item_{i}',s,x,y,8.6)
# Retain the source's process-evaluation relation without complex paths.
for i,y in enumerate([34,270]):
 rect(f'evaluation_arrow_stem_{i}',335,y-2.6,6,5.2,'#6EB8BA')
 poly(f'evaluation_arrow_head_{i}',[[330,y],[336,y-5],[336,y+5]],'#6EB8BA')
for i,c in enumerate('开源创新全流程评价'):
 text(f'process_evaluation_char_{i}',c,336.5,119+i*9.1,8.2,MUTED,500)

svg=['<?xml version="1.0" encoding="UTF-8"?>','<svg xmlns="http://www.w3.org/2000/svg" width="493pt" height="300pt" viewBox="0 0 493 300">','<title>开源创新工作的协同框架</title>','<desc>依据用户提供《中国科协联合国咨商开源创新专委会介绍(1).pdf》第2页工作体系图重绘。所有文字均为可编辑文本。</desc>']
for e in elems:
 if e['type']=='rect':
  a=f'<rect id="{e["id"]}" x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" fill="{e["fill"]}"'
  if 'stroke' in e:a+=f' stroke="{e["stroke"]}" stroke-width="{e["stroke_width"]}"'
  svg.append(a+'/>')
 elif e['type']=='line':svg.append(f'<line id="{e["id"]}" x1="{e["x1"]}" y1="{e["y1"]}" x2="{e["x2"]}" y2="{e["y2"]}" stroke="{e["color"]}" stroke-width="{e["stroke_width"]}"/>')
 elif e['type']=='polygon':svg.append(f'<polygon id="{e["id"]}" points="'+ ' '.join(f'{x},{y}' for x,y in e['points'])+f'" fill="{e["fill"]}"/>')
 elif e['type']=='text':svg.append(f'<text id="{e["id"]}" x="{e["x"]}" y="{e["y"]}" font-family="Noto Sans CJK SC" font-size="{e["size"]}" font-weight="{e["weight"]}" fill="{e["color"]}" text-anchor="{e["anchor"]}">{html.escape(e["text"])}</text>')
svg.append('</svg>')
(P/'ccosi-work-system.svg').write_text('\n'.join(svg),encoding='utf-8')
meta={'title':'开源创新工作的协同框架','version':'v0.2','canvas':{'width':493,'height':300,'viewBox':[0,0,493,300],'unit':'pt','coordinate_system':'top-left origin; text y is alphabetic baseline'},'source':{'pdf':'中国科协联合国咨商开源创新专委会介绍(1).pdf','page':2,'image_xref':107},'min_font_size':min(e['size'] for e in elems if e['type']=='text'),'font_family':'Noto Sans CJK SC','elements':elems,'visible_texts':[e for e in elems if e['type']=='text'],'notes':['全部原工作框架条目保留；图示工作领域与评价维度，不是实证结果。','纵向“开源创新全流程评价”按单字文本分别定位，方便原生PDF复绘。','全部坐标以pt为单位；将SVG平移放入PDF时，应保持比例并使用对应中文字体。']}
(P/'ccosi-work-system.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print('elements',len(elems),'texts',len(meta['visible_texts']),'minimum font',meta['min_font_size'])
