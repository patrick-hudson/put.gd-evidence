from pathlib import Path
import json
b=Path('/tmp/pr1414r2');rows=[]
for h in ['d69','k72','m74','f44']:
 for name in ['file-1m','file-8m']:
  rr=[]
  for kind in ['pr','nc']:
   p=b/h/kind/('combined-results.json' if h=='d69' and kind=='pr' else 'results.json')
   d=json.loads(p.read_text()) if p.exists() else {}
   r=next((x for x in d.get('results',[]) if x['name']==name),{})
   valid=r.get('state')=='completed' and not r.get('timingSource')
   if valid:
    sec=r['seconds'];rr.append(f'<div class="barrow"><span>{"PR" if kind=="pr" else "Nightly"}</span><div class="track"><div style="width:{sec/16*100:.2f}%;background:var(--chart-{1 if kind=="pr" else 2})"></div></div><b>{sec:.2f} s</b></div>')
   else:rr.append(f'<div class="missing">{"PR" if kind=="pr" else "Nightly"}: {"CLI timing lost" if r.get("timingSource") else r.get("state","not run")}</div>')
  rows.append(f'<section><strong>{h} · {name}</strong>'+''.join(rr)+'</section>')
html='''<!doctype html><meta charset="utf-8"><style>body{font-family:var(--font-sans);color:var(--foreground)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}section{padding:16px;border-radius:var(--radius);background:var(--card)}.barrow{display:flex;align-items:center;gap:8px;margin-top:10px;font-size:13px}.barrow>span{width:44px}.barrow>b{width:54px;text-align:right}.track{flex:1;height:16px;background:var(--secondary)}.track>div{height:16px}.missing{color:var(--muted-foreground);font-size:13px;margin-top:10px}p{font-size:13px;color:var(--muted-foreground)}</style><div class="grid">'''+''.join(rows)+'''</div><p>Invocation to terminal state; one sample per case/build. Fixed 0–16 s scale. Failed or lost samples are omitted. Nightly 26.1111.4633; PR ec6e6a136. PR ran first, followed immediately by nightly on each host.</p>'''
(b/'timing-comparison.html').write_text(html)
