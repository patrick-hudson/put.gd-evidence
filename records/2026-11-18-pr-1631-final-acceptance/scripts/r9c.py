import sys,json,zipfile,re;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
O=os.path.expanduser('~/work/qr1618/state/out/')
cancel(open(O+'current-op').read().strip())
terms=["Patrick Hudson","build-host-7","Zebrafish Quartz",r"#\d{4}",r"ZQX-\d{3}","Zebrafish","Quartz","ZQX","quickRedactTerms","quickRedactPatterns"]
out={}
for inc in (False,True):
    p=O+'bundle3-%s.zip'%('names' if inc else 'nonames')
    t=time.time()
    r=cli('diagnostics.bundle',{'output':p,'includeNames':inc,'since':'7d'},timeout=700)
    print('bundle includeNames=',inc,'ok',r.get('ok'),'secs',round(time.time()-t,1),json.dumps(r.get('result') or r.get('error'))[:300])
    z=zipfile.ZipFile(p); names=z.namelist()
    hits={k:[] for k in terms}; cfg=None; nfiles=0
    for n in names:
        if n.endswith('/'): continue
        nfiles+=1
        b=z.read(n)
        if 'config' in n and n.endswith('.json') and b'preferences' in b: cfg=(n,b.decode())
        for k in terms:
            if k.encode().lower() in b.lower(): hits[k].append(n)
    out[str(inc)]={'files':nfiles,'hits':{k:v for k,v in hits.items() if v}}
    print(' files',nfiles,'hits',json.dumps({k:v for k,v in hits.items() if v}))
    if cfg:
        d=json.loads(cfg[1]); print(' ',cfg[0],'preferences=',json.dumps(d.get('preferences')))
json.dump(out,open(O+'r9c-diagnostics.json','w'),indent=1)
