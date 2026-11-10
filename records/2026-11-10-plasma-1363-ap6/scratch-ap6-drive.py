import sys,os,json,time
from pathlib import Path
sys.argv=['drive','ap6','/home/patrick/work/put.gd/work/lab-bootstrap-k72/identity','kde']+sys.argv[1:]
exec(compile(Path('/tmp/p1363-checks.py').read_text().split('build = cli(')[0],'/tmp/p1363-checks.py','exec'))
E=Path(ROOT)/'work/acceptance-1363/ap6';E.mkdir(parents=True,exist_ok=True)
def save(n,v):
 (E/(n+'.json')).write_text(json.dumps(v,indent=2));return v
def shot(n,h=0):dump(h).save(E/(n+'.png'))
def key(*k):return lab('key','--run',RUN,*k)
def patch(p):
 d=cli('settings.get');return cli('settings.patch',{'patch':p,'expectedRevision':d['metadata']['observedRevision']})
def show(v):cli('ui.show',{'view':v});time.sleep(2)
exec(sys.argv[4])
