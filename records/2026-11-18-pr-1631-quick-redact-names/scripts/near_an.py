import sys,json
d=json.load(open(sys.argv[1]));w=json.load(open(sys.argv[2]))
x0,y0,x1,y1=map(int,sys.argv[3:7])
def inr(r): return r[0]>=x0 and r[0]+r[2]<=x1 and r[1]>=y0 and r[1]+r[3]<=y1
def ov(a,b): return max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))
marks=[(c['rect'],c['suggested']) for c in d['covered']]
rows={}
for x in w:
    if not inr(x['rect']): continue
    cat=[s for r,s in marks if ov(x['rect'],r)>0.5*x['rect'][2]*x['rect'][3]]
    rows.setdefault(x['rect'][1]//22,[]).append((x['rect'][0],x['text'],cat[0] if cat else '.'))
for k in sorted(rows): print(' '.join(f"{t}[{c}]" if c!='.' else t for _,t,c in sorted(rows[k])))
