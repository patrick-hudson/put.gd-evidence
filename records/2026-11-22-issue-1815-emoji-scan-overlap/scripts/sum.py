import json,sys
def rows(d):
    t=open(d+'/rows.json').read().strip()
    return json.loads(t) if t.startswith('[') else [json.loads(x) for x in t.splitlines() if x.strip()]
for d in sys.argv[1:]:
    s=json.load(open(d+'/summary.json'))
    print(d,'captures',s.get('captures'),'failed',s.get('failed'))
    for g in ('all','screens_1080p','screens_4k','regions'):
        x=s.get(g) or {}
        print(' ',g,{k:x.get(k) for k in ('n','wall_sum','wall_p50','peak_max_KiB','cer_median','cer_pooled','cer_vs_ref_median')})
    r=rows(d); diff=[x['id'] for x in r if x.get('cer_vs_ref') not in (0,0.0,None)]
    print('  text differs from reference:',len(diff),diff[:8])
