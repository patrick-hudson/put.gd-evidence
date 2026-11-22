import json,sys,collections
JWT={0,2,3,4,6}
def load(f):
    d=json.load(open(f));det={};per={}
    for r in d["rows"]:
        k=(r["font"],r["px"],r["theme"])
        if r["code"]=="detail":det[k]=r
        else:
            for l in r["lines"]:per[k+(l["line"],)]=l
    return d["summary"],det,per
def inter(a,b):
    return a[0]<b[0]+b[2] and b[0]<a[0]+a[2] and a[1]<b[1]+b[3] and b[1]<a[1]+a[3]
def heads(det):
    out={}
    for k,r in det.items():
        tr=r["truth"]
        for t in tr:
            if not t["m"] or t["line"] not in JWT:continue
            c=[x for x in r["candidates"] if inter(x["r"],t["ink"])]
            c.sort(key=lambda x:x["r"][0])
            out[k+(t["line"],)]=(c[0]["t"] if c else None)
    return out
def stats(f,verbose=False):
    s,det,per=load(f);h=heads(det)
    tab=collections.Counter();starts=collections.Counter();nb=collections.Counter()
    for k,l in per.items():
        line=k[3]
        if line in JWT:
            tab["cases"]+=1
            if l["leaked"]<0:tab["notfound"]+=1
            elif l["leaked"]>0:tab["leak"]+=1
            if l["neighbourInk"]>0:tab["jwtline neighbour"]+=1
            hd=h.get(k)
            st=(hd or "")[:5]
            starts[st[:st.find("ey")+3] if "ey" in st else st]+=1
        elif l["neighbourInk"]>0:nb[line]+=1
    # over-cover on plain lines: matches containing words from lines 1,5,7
    plainhits=collections.Counter()
    for k,r in det.items():
        for m in r["matches"]:
            ys=[b[1] for b in m["boxes"]]
            plainhits[m["category"]]+=0
    return s,tab,starts,nb
def notfound(f):
    s,det,per=load(f);h=heads(det)
    return {k:h.get(k) for k,l in per.items() if k[3] in JWT and l["leaked"]<0}
if __name__=="__main__":
    for f in sys.argv[1:]:
        s,tab,starts,nb=stats(f)
        print(f,json.dumps(s["marks"]),dict(tab),"plain-line neighbour",dict(nb))
        print("  heads",starts.most_common(30))
def overcover(f):
    s,det,per=load(f);out=collections.Counter();ex=[]
    for k,r in det.items():
        for m in r["matches"]:
            for b,t in zip(m["boxes"],m["text"].split(' ')):
                cx,cy=b[0]+b[2]/2,b[1]+b[3]/2
                for w in r["truth"]:
                    i=w["ink"]
                    if not w["m"] and i[0]-1<=cx<=i[0]+i[2]+1 and i[1]-1<=cy<=i[1]+i[3]+1:
                        out[(w["line"],w["t"])]+=1;ex.append((k,w["t"],t))
    return out,ex
if __name__=="__main__":
    for f in sys.argv[1:]:
        o,ex=overcover(f);print("  overcover",sum(o.values()),o.most_common(20))
