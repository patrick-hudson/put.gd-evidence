from pathlib import Path
exec((Path.cwd()/'batch.py').read_text().split('host=sys.argv[1]')[0])
def force(b,d,wheel,seed):
 samples=[]
 def sample():
  v=A.rpc('scroll.inspect',{'id':d.sid});samples.append(dict(y=b.js(S.POS),view=v));return v
 wheel('w 8');time.sleep(1)
 wheel('w 60');time.sleep(.8);v=sample()
 for _ in range(5):
  if v.get('activity')=='lost':break
  wheel('w 30');time.sleep(.1);v=sample()
 for _ in range(400):
  if v.get('activity')!='lost':break
  wheel('w -1');time.sleep(.18);v=sample()
 (d.out/'forced-recovery.json').write_text(json.dumps(samples,indent=1));d.stop.touch()
S.person=force
os.environ['LAB_TAG']='D-forced-2';os.environ['SFR_WHEEL_DELAY']='0.001';os.environ['LAB_NAV_JS']='0'
q=A.rpc('scroll.prepare',{'rect':[240,200,1440,700]});A.rpc('scroll.cancel',{'id':q['id']})
mouse=subprocess.Popen(['sudo','-n','env','SFR_WHEEL_DELAY=0.001','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready')
def wheel(s):mouse.stdin.write(s+'\n');mouse.stdin.flush()
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 import inspect
 source=inspect.getsource(L.browser_start).replace("'browser.tabs.warnOnClose': False","'general.smoothScroll': False, 'browser.tabs.warnOnClose': False");exec(source,L.__dict__)
 L.browser_start('firefox');S.run('firefox','wiki','user',wheel)
finally:L.browser_stop();wheel('q');mouse.wait(5)
