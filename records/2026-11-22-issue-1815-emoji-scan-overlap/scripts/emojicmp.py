import json,sys
def load(p):
    d={}
    for l in open(p):
        x=json.loads(l); d.setdefault(x['image'],[]).append(x)
    return d
a=load(sys.argv[1]); b=load(sys.argv[2])
same=0;diff=[];emojis=0
for k in sorted(a):
    ta={x['text'] for x in a[k]}; tb={x['text'] for x in b.get(k,[])}
    if ta==tb and len(ta)==1: same+=1
    else: diff.append(k)
    emojis+=len(a[k][0]['emoji'])
print('images',len(a),'identical (all runs)',same,'differ',diff,'emoji chars per pass',emojis)
for k in sorted(a): print(' ',k,a[k][0]['emoji'],'|',b[k][0]['emoji'] if k in b else None, max(x['peakKiB'] or 0 for x in a[k]), max(x['peakKiB'] or 0 for x in b.get(k,[{'peakKiB':0}])))
