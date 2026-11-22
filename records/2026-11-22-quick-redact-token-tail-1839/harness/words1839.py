import json,sys,collections,re
ordinary=re.compile(r"^\(?(was|leaked|today|expires|next|week|rotated)\)?\.?$",re.I)
def run(f):
    d=json.load(open(f));c=collections.Counter();ex=[]
    for r in d["rows"]:
        if r["code"]!="detail": continue
        for m in r["matches"]:
            if m["category"]!="key": continue
            ws=m["text"].split(' ')
            extra=[w for w in ws if ordinary.match(w)]
            c["key matches"]+=1
            c["with ordinary words"]+=bool(extra)
            c["ordinary words covered"]+=len(extra)
            if extra and len(ex)<40: ex.append(m["text"])
    return c,ex
for f in sys.argv[1:]:
    c,ex=run(f);print(f.split('/')[-2],dict(c))
    if 'f18' in f:
        for e in collections.Counter(ex).most_common(20):print("   ",e)
