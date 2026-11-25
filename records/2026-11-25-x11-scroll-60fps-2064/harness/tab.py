import json,glob,os,sys
rows=[]
for f in sorted(glob.glob(os.path.expanduser('~/work/x2064/lab/runs/*/result.json'))):
    r=json.load(open(f)); c=r.get('capture') or {}; st=c.get('stats') or {}; m=r.get('meter') or {}
    n=r['name']; b='cand1' if 'cand1' in n else 'count' if 'count' in n else 'nightly'
    rows.append((n,b,c.get('endReason'),c.get('height'),r['after']['docHeight'],c.get('framesSkipped'),c.get('foundAgain'),st.get('framesPerSecond'),m.get('helperCpuPct'),m.get('xorgCpuPct'),m.get('peakRssMiB'),(st.get('sourceRate') or {}).get('fallback')))
for x in rows: print("%-44s %-14s %6s/%-6s sk=%-4s fa=%-2s fps=%-5s cpu=%-5s xorg=%-5s rss=%-6s %s"%(x[0],x[2],x[3],x[4],x[5],x[6],x[7],x[8],x[9],x[10],x[11] or ''))
import collections
agg=collections.defaultdict(lambda:[0,0,0,0])
for x in rows:
    if 'user' not in x[0]: continue
    k=(x[1],'brisk' if ('brisk' in x[0] or '-b' in x[0].split('user-')[1]) else 'normal')
    a=agg[k]; a[0]+=1; a[1]+=x[6] or 0; a[2]+= 1 if (x[6] or 0)>0 else 0; a[3]+= max(0,x[4]-x[3])
for k,v in sorted(agg.items()): print(k, "runs",v[0],"losses",v[1],"runs-with-loss",v[2],"rows-short",v[3])
