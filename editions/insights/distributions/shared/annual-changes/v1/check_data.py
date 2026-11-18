#!/usr/bin/env python3
"""Reconcile the shared charts with archived observations, not chart labels."""
from pathlib import Path
import csv, hashlib, json, math

R=Path(__file__).resolve().parent
def js(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open()))
def equal(a,b):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-6),(a,b)

def main():
    m=js(R/'manifest.json');d=js(R/'shared/chart-data.json');ev=R/'shared/evidence'
    assert hashlib.sha256((R/'shared/chart-data.json').read_bytes()).hexdigest()==m['shared_data_sha256']
    assert set(d)==set(map(str,range(1,9)))
    prose={}
    for language in ['zh-CN','en']:
        content=js(R/m['languages'][language]['content'])
        prose[language]=[item for page in content['pages'] for item in page['items']]
        assert len(content['pages'])==2
        assert [item['id'] for page in content['pages'] for item in page['items']]==list(range(1,9))
        assert all(len(page['items'])==4 for page in content['pages'])
        assert all(item.get(key) for page in content['pages'] for item in page['items'] for key in ['chart_title','scope','title','body'])
    alignment=js(R/'shared/bilingual-alignment.json')['units']
    assert len(alignment)==8
    for i,unit in enumerate(alignment):
        assert unit['source_unit_id']==f'annual_shift_{i+1:02}'
        for lang,key in [('zh-CN','source_sha256'),('en','translation_sha256')]:
            raw=json.dumps(prose[lang][i],ensure_ascii=False,sort_keys=True).encode()
            assert hashlib.sha256(raw).hexdigest()==unit[key],(lang,i+1,'translation alignment drift')
    for s in js(R/'shared/source-records.json')['local_snapshots']:
        assert hashlib.sha256((ev/s['file']).read_bytes()).hexdigest()==s['sha256'],s['file']
    assert [round(r['values'][2]/r['values'][1],2) for r in d['1']['rows']]==[2.67,2.66,3.24,2.42]
    assert round((2.96/2.43-1)*100,1)==d['2']['rows'][1]['growth']
    assert round((1/.711-1)*100,1)==d['2']['rows'][2]['growth']
    active=rows(ev/'five_groups_active_trend.csv')
    for chart,key in zip(d['3']['rows'],['中国','印度','全球南方代表国家']):
        vals=[float(next(r for r in active if int(r['year'])==year)[key]) for year in d['3']['years']]
        for actual,expected in zip(chart['values'],vals):equal(actual,expected)
        equal(chart['growth'],100*(vals[1]/vals[0]-1))
    contribution=rows(ev/'five_groups_contribution.csv')
    for chart,key in zip(d['4']['rows'],['China','United States']):
        for actual,row in zip(chart['values'],contribution):equal(actual,float(row[key]))
    for chart in d['6']['rows']:
        for i,month in enumerate(d['6']['months']):
            raw=next(r for r in js(ev/f'board-initiator-{month}.json')['data'] if r['id']==chart['id'])
            equal(chart['values'][i],raw['openrank']);assert chart['ranks'][i]==raw['rank']
    for chart in d['7']['rows']:
        for i,month in enumerate(d['7']['months']):
            raw=js(ev/f'board-foundation-{month}.json')['data']
            if chart['id']==':foundations/linux_foundation':
                selected=[r for r in raw if r['id'].startswith(chart['id'])]
                assert len(selected)==d['7']['lf_label_count']
                expected=sum(r['openrank'] for r in selected)
            else:expected=next(r['openrank'] for r in raw if r['id']==chart['id'])
            equal(chart['values'][i],expected)
    cohort=[r for r in rows(ev/'agentic-ai-projects.csv') if r['landscape_action'] in ['keep','add'] and r['landscape_layer']=='Agent Infra']
    assert len(cohort)==d['8']['total']==86
    assert sum(r['created_at']>='2025-01-01' for r in cohort)==d['8']['created_since_2025']==48
    for category in d['8']['categories']:
        sample=[r for r in cohort if r['landscape_section']==category['id']]
        assert len(sample)==category['total']
        assert sum(r['created_at']>='2025-01-01' for r in sample)==category['recent']
    assert len(d['8']['categories'])==12
    print('PASS: two languages × eight stories; shared input hashes; regional series; six monthly snapshots; 48/86 repository creation cohort.')
    print('Scope: archived-data reconciliation, not a new upstream data audit or causal test.')

if __name__=='__main__':main()
