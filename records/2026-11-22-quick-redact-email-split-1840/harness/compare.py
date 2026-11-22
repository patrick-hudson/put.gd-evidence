import json,sys,collections
def load(f):
    d=json.load(open(f));per={};det={}
    for r in d["rows"]:
        k=(r["font"],r["px"],r["theme"])
        if r["code"]=="detail": det[k]=r
        else:
            for l in r["lines"]: per[k+(l["line"],)]=l
    return d["summary"],per,det
names=["email sentence","email end of line","email after a sentence dot","email with initials","token was leaked today","token (expires next week).","stripe was rotated"]
sa,pa,da=load(sys.argv[1]);sb,pb,db=load(sys.argv[2])
print("A",json.dumps(sa));print("B",json.dumps(sb))
tab=collections.defaultdict(lambda:collections.Counter())
changes=[]
for k in sorted(pa):
    a=pa[k];b=pb[k];n=names[k[3]]
    t=tab[n];t["cases"]+=1
    for tag,x in (("A",a),("B",b)):
        if x["leaked"]<0:t[tag+" missed"]+=1
        elif x["leaked"]>0:t[tag+" leak"]+=1
        if x["neighbourInk"]>0:t[tag+" neighbour"]+=1
    if (a["leaked"]>0)!=(b["leaked"]>0) or (a["neighbourInk"]>0)!=(b["neighbourInk"]>0) or (a["leaked"]<0)!=(b["leaked"]<0):
        changes.append((k,n,a,b))
for n in names:
    print(n,dict(tab[n]))
def text(det,k):
    return [m["category"]+": "+m["text"] for m in det[k[:3]]["matches"]]
for k,n,a,b in changes:
    cand=[c["t"] for c in da[k[:3]]["candidates"]]
    print(k,n,"A",a["leaked"],a["neighbourInk"],"B",b["leaked"],b["neighbourInk"])
    print("   A",[t for t in text(da,k)], "\n   B",[t for t in text(db,k)])
