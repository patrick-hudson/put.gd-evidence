import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
def patch(p):
    g=res('settings.get'); rev=g['metadata']['observedRevision']
    r=cli('settings.patch',{'patch':{'preferences':p},'expectedRevision':rev})
    return r.get('ok'),(r.get('error') or {}).get('message')
def cfg(): return json.load(open(os.path.expanduser('~/work/qr1618/state/config/putgd/config.json')))['preferences']
print('two words ->',patch({'quickRedactTerms':['projectalpha','ProjectAlpha']})); print(' config:',cfg().get('quickRedactTerms'))
for n,p in (('500 spaces + x (501 chars)',' '*500+'x'),('499 spaces + x (500 chars)',' '*499+'x'),('x*500','x'*500),('x*501','x'*501)):
    before=cfg().get('quickRedactPatterns')
    print(n,'->',patch({'quickRedactPatterns':[p]}),'| config changed:',cfg().get('quickRedactPatterns')!=before)
print(' final patterns lens:',[len(x) for x in cfg().get('quickRedactPatterns',[])])
