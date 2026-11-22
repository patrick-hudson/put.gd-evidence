import json,sys
LINES=["card","token","email-sentence","card-start","email-end"]
def load(p):
    d=json.load(open(p));out={}
    for r in d["rows"]:
        if r["code"]!="shipped":continue
        for l in r["lines"]:out[(r["font"],r["px"],r["theme"],l["line"])]=l
    return d["summary"],out
sa,a=load(sys.argv[1]);sb,b=load(sys.argv[2])
for n,s in (("A",sa),("B",sb)):print(n,json.dumps(s["shipped"]),"missed",s["missedByRecognition"],"/",s["expectedMatches"])
def tally(m):
    leak=sum(1 for v in m.values() if v["leaked"]>0);nb=sum(1 for v in m.values() if v["neighbourInk"]>0)
    return leak,nb
print("A leakCases,nbCases",tally(a),"B",tally(b))
show=sys.argv[3] if len(sys.argv)>3 else "diff"
for k in sorted(a):
    x,y=a[k],b.get(k)
    if y is None:continue
    if show=="leakB" and y["leaked"]>0: print("LEAK",k,LINES[k[3]],y["who"])
    if show=="nbB" and y["neighbourInk"]>0: print("NB",k,LINES[k[3]],y["who"])
    if show=="diff" and ((x["leaked"]>0)!=(y["leaked"]>0) or (x["neighbourInk"]>0)!=(y["neighbourInk"]>0)):
        print(k,LINES[k[3]],"A:",x["leaked"],x["neighbourInk"],x["who"]," B:",y["leaked"],y["neighbourInk"],y["who"])
