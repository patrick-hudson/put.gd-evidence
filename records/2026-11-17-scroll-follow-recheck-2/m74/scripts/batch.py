import accept as A,os,sys,time,json,random,subprocess,re,importlib.util
from pathlib import Path
P=A.P;os.chdir(P)
spec=importlib.util.spec_from_file_location('pages',P/'pages-relative.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M);S=M.S;L=A.L
# Real wheel batches all the way down, without the historical automatic recovery loop.
def person(b,d,wheel,seed):
 rng=random.Random(seed);up=False;end=None;beg=time.time();samples=[]
 while d.running() and time.time()-beg<480:
  y,h,doc=b.js(S.POS);v=A.rpc('scroll.inspect',{'id':d.sid});samples.append({'y':y,'doc':doc,'activity':v.get('activity'),'height':v.get('height'),'time':time.time()})
  if y+h>=doc-2:
   end=end or time.time()
   if time.time()-end>3:break
   wheel('w 2');time.sleep(.6);continue
  end=None
  if os.environ.get('RECHECK_NEWS')=='1'and not up and y>.48*(doc-h):
   wheel('w -6');up=True;time.sleep(2);continue
  wheel('w %d'%rng.choice([1,2,3,3,4,5]));time.sleep(rng.uniform(.22,.5))
 (d.out/'scroll-samples.json').write_text(json.dumps(samples,indent=1));d.stop.touch()
S.person=person
# Final round: capture the actual desktop notice before reference screenshots.
orig_running=M.Driver.running
def running(d):
 was=d.end is not None
 r=orig_running(d)
 if not r and not was and d.last.get('state')=='done':
  (d.out/'scroll-inspect.json').write_text(json.dumps(A.rpc('scroll.inspect',{'id':d.sid}),indent=1))
  time.sleep(.7);S.desk(d.out/'desktop-notice.png')
 return r
M.Driver.running=running
# Inspect and bind archive by the helper's exact digest, never newest-file fallback.
def sync_artifact(sid):
 import hashlib
 v=A.rpc('scroll.inspect',{'id':sid});expected=v['result']['sha256']
 for _ in range(100):
  for f in (P/'archive').rglob('*.png'):
   if hashlib.sha256(f.read_bytes()).hexdigest()==expected:return
  time.sleep(.1)
 raise RuntimeError('Exact admitted image missing: '+sid)
A.sync_artifact=sync_artifact
original_person=person
def paced(b,d,wheel,seed):
 if os.environ.get('SFR_FAST')!='1':return original_person(b,d,wheel,seed)
 start=time.time();samples=[];end=None
 while d.running() and time.time()-start<180:
  y,h,doc=b.js(S.POS);v=A.rpc('scroll.inspect',{'id':d.sid});samples.append(dict(y=y,doc=doc,activity=v.get('activity'),time=time.time()))
  if y+h>=doc-2:
   end=end or time.time()
   if time.time()-end>3:break
   time.sleep(.3);continue
  wheel('w 18');time.sleep(.06)
 (d.out/'scroll-samples.json').write_text(json.dumps(samples,indent=1));d.stop.touch()
S.person=paced
host=sys.argv[1]
cases=([('A','firefox','github','user',8),('Afast','firefox','github','user',3),('Bso','firefox','stackoverflow','user',2),('Bnews','firefox','news','user',2),('Bwiki','firefox','wiki','user',1),('Bwiki','firefox','wiki','auto',1)]if host=='m74'else[('Cff','firefox','github','user',3),('Cchrome','chromium','github','user',1),('Cwiki','firefox','wiki','user',1),('Cwiki','firefox','wiki','auto',1),('Cauto','firefox','github','auto',1)])
for case,kind,site,mode,n in cases:
 for i in range(1,n+1):
  tag=case+'-'+str(i)
  existing=P/'runs'/(f'{kind}-{site}-{mode}-'+tag)
  if (existing/'result.json').exists()or (P/'runs'/tag/'process.json').exists():continue
  os.environ['SFR_FAST']='1'if case=='Afast'else'0';os.environ['SFR_WHEEL_DELAY']='0.001'if case=='Afast'else'0.012';os.environ['LAB_TAG']=tag;os.environ['RECHECK_NEWS']='1'if site=='news'else'0';os.environ['LAB_NAV_JS']='1'if site=='news'else'0'
  if site=='blank':
   # Existing exact gap proof with distinct per-run files and result.
   log=(P/(tag+'.log')).open('w');q=subprocess.run([sys.executable,str(P/'default-blank-proof.py')],stdout=log,stderr=subprocess.STDOUT);log.close()
   out=P/'runs'/tag;out.mkdir(parents=True,exist_ok=True)
   for f in P.glob('blank-default-*'):
    if f.is_file():f.rename(out/f.name)
   (out/'process.json').write_text(json.dumps({'exit':q.returncode}));print(tag,q.returncode,flush=True);continue
  # Close only this resident's prior notices before native calibration.
  prep=A.rpc('scroll.prepare',{'rect':[240,200,1440,700]});A.rpc('scroll.cancel',{'id':prep['id']});time.sleep(.5)
  mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready')
  def wheel(s):mouse.stdin.write(s+'\n');mouse.stdin.flush()
  try:
   profile=P/('profile-'+kind)
   if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
   if site=='stackoverflow':
    import shutil
    shutil.copytree(P/'so-profile',profile)
    import inspect
    src=inspect.getsource(L.browser_start).replace('if prof.exists():',"if prof.exists() and os.environ.get('SFR_REUSE_PROFILE')!='1':").replace('prof.mkdir(mode=0o700)','prof.mkdir(mode=0o700,exist_ok=True)');exec(src,L.__dict__);os.environ['SFR_REUSE_PROFILE']='1'
   else:os.environ.pop('SFR_REUSE_PROFILE',None)
   L.browser_start(kind)
   if kind=='chromium'and site=='python':b,_=L.connect();b.cmd('Emulation.setEmulatedMedia',{'features':[{'name':'prefers-color-scheme','value':'dark'}]})
   if site=='blank':S.PAGES['blank']='file://'+str(P/'blank.html')
   S.run(kind,site,mode,wheel)
  except Exception as e:
   (P/(tag+'-error.txt')).write_text(repr(e));print(tag,repr(e),flush=True)
  finally:
   L.browser_stop();wheel('q');mouse.wait(5)
print('BATCH COMPLETE',flush=True)
