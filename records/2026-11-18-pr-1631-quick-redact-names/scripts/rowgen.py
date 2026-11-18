import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
name=sys.argv[1]; cats=sys.argv[2].split(','); kw={}
if len(sys.argv)>3: kw=json.loads(sys.argv[3])
rep,ins=capture_redact(name,cats,**kw)
print(json.dumps({k:rep[k] for k in rep if k not in('shapes','apply')}|{'counts':(rep['apply'] or {}).get('counts'),'apply_err':None if rep.get('ok') else rep['apply']},indent=1))
