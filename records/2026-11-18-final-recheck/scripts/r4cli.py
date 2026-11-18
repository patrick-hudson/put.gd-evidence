import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
def tryp(p):
    g=res('settings.get'); rev=g['metadata']['observedRevision']
    r=cli('settings.patch',{'patch':{'preferences':{'quickRedactPatterns':p}},'expectedRevision':rev})
    return r.get('ok'),(r.get('error') or {}).get('message'),(r.get('error') or {}).get('code')
for p in (['(a+)+$'],['(foo|bar)+'],[r'\bJIRA-\d+\b'],[r'#\d{4}',r'(?i)\bquick\sredact\b']):
    print(json.dumps(p),'->',tryp(p))
print(json.dumps(res('settings.get')['document']['preferences'].get('quickRedactPatterns')))
