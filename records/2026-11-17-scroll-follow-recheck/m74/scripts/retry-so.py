from pathlib import Path
import os,time,random,subprocess,importlib.util,inspect,json
P=Path.cwd();os.environ['LAB_TAG']='A2-2';os.environ['SFR_REUSE_PROFILE']='1'
spec=importlib.util.spec_from_file_location('pages',P/'pages-relative.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M);A=M.A;L=M.L;S=M.S
profile=P/'profile-firefox'
if profile.exists():profile.rename(P/(profile.name+'-before-so-retry-'+str(time.time_ns())))
source=P/'profile-firefox-1794879260126568777';assert source.is_dir();source.rename(profile)
s=inspect.getsource(L.browser_start).replace('if prof.exists():',"if prof.exists() and os.environ.get('SFR_REUSE_PROFILE')!='1':").replace('prof.mkdir(mode=0o700)','prof.mkdir(mode=0o700,exist_ok=True)');exec(s,L.__dict__)
old=L.wait_loaded
def loaded(b,*a,**kw):
 v=old(b,*a,**kw)
 if v.get('title')=='Just a moment...':
  time.sleep(20);v=b.js(L.INFO)
  if v.get('title')=='Just a moment...':raise RuntimeError('SITE BLOCKED: Cloudflare challenge; no question-page capture started')
 return v
L.wait_loaded=loaded
# The same one-way real wheel driver, with no recovery loop or reversal for SO.
spec=importlib.util.spec_from_file_location('batchsource',P/'batch.py')
source=(P/'batch.py').read_text();part=source[source.index('def person('):source.index('S.person=person')];exec(part,globals());S.person=person
mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready')
def wheel(s):mouse.stdin.write(s+'\n');mouse.stdin.flush()
try:
 L.browser_start('firefox');S.run('firefox','stackoverflow','user',wheel)
finally:L.browser_stop();wheel('q');mouse.wait(5)
