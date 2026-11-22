import sys,collections;sys.path.insert(0,sys.path[0]);import jwtstat as j
a=j.load(sys.argv[1]);b=j.load(sys.argv[2]);ha=j.heads(a[1])
st=lambda l:"miss" if l["leaked"]<0 else ("leak" if l["leaked"]>0 else "ok")
t=collections.Counter();ex=collections.defaultdict(list)
for k,la in a[2].items():
    if k[3] not in j.JWT:continue
    lb=b[2][k];x=(st(la),st(lb));t[x]+=1;ex[x].append((k,la["leaked"],lb["leaked"],(ha.get(k) or "")[:10]))
print(dict(t))
for x in [("ok","leak"),("leak","ok"),("miss","leak"),("leak","miss"),("ok","miss")]:
    print(x,ex[x][:12])
