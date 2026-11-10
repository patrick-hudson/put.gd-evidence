import sys,subprocess,json,shlex
from pathlib import Path
from importlib.machinery import SourceFileLoader
c=SourceFileLoader('c','/tmp/p1363-campaign.py').load_module();d=sys.argv[1];h,r,*_=c.PROFILES[d];r=sys.argv[2] if len(sys.argv)>2 and sys.argv[2]!='--failed' else r;failed='--failed' in sys.argv;e='/home/patrick/work/i1363/work/acceptance-1363/'+r
script='''import json,hashlib,shutil
from pathlib import Path
r=Path.home()/'work/i1363/work/lab-runs'/RUN
out=Path.home()/'work/i1363/work/acceptance-1363'/RUN
if not FAILED:
 log=(out/'checks.log').read_text();assert '# 0 failed' in log and log.count('ok  ')>=15,log
 if (out/'gui-ready.json').exists():
  assert (out/'gui-results.json').exists(), 'GUI outcomes must be reviewed and recorded before passed retirement'
  gui=json.loads((out/'gui-results.json').read_text());assert gui.get('completed') and gui.get('passed'),gui
else:assert (out/'failure.txt').exists()
state=json.loads((r/'state.json').read_text())
for source in r.glob('install-*/*'):
 if source.name in ['apt.log','result.json','supervisor.log']:shutil.copyfile(source,out/(source.parent.name+'-'+source.name))
from PIL import Image
for source in r.glob('guest-preflight-*.ppm'):Image.open(source).save(out/(source.stem+'.png'))
for name in ['package.json','layout.json','qmp-features.json']:
 if (r/name).exists():shutil.copyfile(r/name,out/name)
(out/'run-identity.json').write_text(json.dumps({k:v for k,v in state.items() if k in ['id','profile','pid','golden','golden_sha256','head_layout','heads','acceleration','overlay']},indent=2))
tmp=Path('/tmp')/('p1363-'+RUN)
for source in tmp.rglob('*.png'):
 shutil.copyfile(source,out/('artifact-'+source.parent.name+'-'+source.name))
(out/'completion.json').write_text(json.dumps({'run':str(r),'runId':state['id'],'completed':True,'outcome':'failed' if FAILED else 'passed'},indent=2))
files={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file() and f.name not in ['cleanup-manifest.json','overlay-cleanup.json']}
(out/'cleanup-manifest.json').write_text(json.dumps({'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence','run':str(r),'runId':state['id'],'completed':True,'outcome':'failed' if FAILED else 'passed','files':files},indent=2))
'''.replace('RUN',repr(r)).replace('FAILED',repr(failed))
c.remote(h,shlex.join(['python3','-c',script]))
target=c.OUT/'base'/d/r;target.mkdir(parents=True,exist_ok=True)
subprocess.run(['rsync','-r','-c','-e',' '.join(c.ssh(h)[:-1]),c.ssh(h)[-1]+':'+e+'/',str(target)+'/'],check=True)
# Export verified, then let the canonical guard inspect processes/backing chains and retire only disk.qcow2.
cmd='cd ~/work/i1363; python3 tools/lab/lab.py cleanup --run work/lab-runs/'+r+' --images-root /home/patrick/work/put.gd/work/lab-images --evidence-manifest '+e+'/cleanup-manifest.json'
c.remote(h,cmd+' --dry-run');c.remote(h,cmd)
subprocess.run(['rsync','-r','-c','-e',' '.join(c.ssh(h)[:-1]),c.ssh(h)[-1]+':/home/patrick/work/i1363/work/lab-runs/'+r+'/overlay-cleanup.json',str(target)+'/overlay-cleanup.json'],check=True)
print('retired',d,flush=True)
