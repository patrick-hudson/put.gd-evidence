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
host=sys.argv[1]
cases=([('A1','firefox','github','user',5),('A2','firefox','stackoverflow','user',2),('A3','firefox','blank','user',3),('A4','firefox','news','user',2),('A5','firefox','wiki','user',1),('A5','firefox','wiki','auto',1)]if host=='m74'else[('B1','firefox','github','user',5),('B2','firefox','news','user',2),('B3','firefox','wiki','user',1),('B3','firefox','wiki','auto',1),('B4','chromium','python','auto',1),('B4','firefox','github','auto',1),('B5','firefox','blank','user',1)])
for case,kind,site,mode,n in cases:
 for i in range(1,n+1):
  tag=case+'-'+str(i)
  existing=P/'runs'/(f'{kind}-{site}-{mode}-'+tag)
  if (existing/'result.json').exists()or (P/'runs'/tag/'process.json').exists():continue
  os.environ['LAB_TAG']=tag;os.environ['RECHECK_NEWS']='1'if site=='news'else'0';os.environ['LAB_NAV_JS']='1'if site=='news'else'0'
  if site=='blank':
   # Existing exact gap proof with distinct per-run files and result.
   log=(P/(tag+'.log')).open('w');q=subprocess.run([sys.executable,str(P/'default-blank-proof.py')],stdout=log,stderr=subprocess.STDOUT);log.close()
   out=P/'runs'/tag;out.mkdir(parents=True,exist_ok=True)
   for f in P.glob('blank-default-*'):
    if f.is_file():f.rename(out/f.name)
   (out/'process.json').write_text(json.dumps({'exit':q.returncode}));print(tag,q.returncode,flush=True);continue
  mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready')
  def wheel(s):mouse.stdin.write(s+'\n');mouse.stdin.flush()
  try:
   profile=P/('profile-'+kind)
   if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
   L.browser_start(kind)
   if kind=='chromium'and site=='python':b,_=L.connect();b.cmd('Emulation.setEmulatedMedia',{'features':[{'name':'prefers-color-scheme','value':'dark'}]})
   if site=='blank':S.PAGES['blank']='file://'+str(P/'blank.html')
   S.run(kind,site,mode,wheel)
  except Exception as e:
   (P/(tag+'-error.txt')).write_text(repr(e));print(tag,repr(e),flush=True)
  finally:
   L.browser_stop();wheel('q');mouse.wait(5)
print('BATCH COMPLETE',flush=True)
