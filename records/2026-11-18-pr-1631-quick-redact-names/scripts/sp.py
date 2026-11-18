import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
a=sys.argv[1]
patch=json.load(open(a[1:])) if a.startswith('@') else json.loads(a)
r=cli('settings.get'); rev=r['result']['metadata']['observedRevision']
r=cli('settings.patch',{'patch':patch,'expectedRevision':rev})
print(json.dumps(r.get('error') if not r.get('ok') else {'ok':True,'validation':r['result']['validation']}))
if r.get('ok'): print(json.dumps(res('settings.get')['document']['preferences']))
