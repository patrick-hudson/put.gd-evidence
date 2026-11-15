import accept as A,json,time,subprocess,sys
from pathlib import Path
P=A.P;L=A.L
# Use this run's own pinned modules, including the VNC port override.
sys.path.insert(0,str(P))
# Reuse the evidence trial, copied beside this driver by setup.
import trial_relative as trial
trial.cli=lambda path,method,params: {'ok':True,'result':A.rpc(method,params)}
orig=trial.flat
trial.os.environ.update(A.E)
def gnome_health(label):
 if not A.E.get('XDG_CURRENT_DESKTOP','').upper().endswith('GNOME'):return None
 e=dict(A.os.environ,XDG_RUNTIME_DIR='/run/user/1000',XDG_CONFIG_HOME=str(Path.home()/'.config'),XDG_DATA_HOME=str(Path.home()/'.local/share'),XDG_STATE_HOME=str(Path.home()/'.local/state'),XDG_CACHE_HOME=str(Path.home()/'.cache'))
 p=subprocess.run(['pgrep','-x','gnome-shell'],capture_output=True,text=True).stdout.split()
 info=subprocess.run(['gnome-extensions','info','putgd@put.gd'],env=e,capture_output=True,text=True)
 import re
 health={'label':label,'shellPids':p,'extensionActive':bool(re.search(r'State:\s+ACTIVE\b',info.stdout)),'extensionInfo':info.stdout,'time':time.time()}
 with (P/'gnome-health.jsonl').open('a') as f:f.write(json.dumps(health)+'\n')
 if len(p)!=1 or not health['extensionActive']:raise RuntimeError('GNOME shell or extension is not active: '+json.dumps(health))
 return p[0]

def run(b):
 rows=[]
 for typ in ['fixed','random']:
  for i in range(10):
   b.js('window.scrollTo({top:0,behavior:"instant"}); return 0;');time.sleep(1)
   # Position from a prior helper log line is fixed for the same rectangle.
   import re
   m=list(re.finditer(r'scroll: bar at .*done (-?\d+),(-?\d+) (\d+)x(\d+)',(P/'helper.log').read_text()))[-1]
   x,y,w,h=map(int,m.groups());stop='auto' if A.E.get('XDG_CURRENT_DESKTOP','').upper().endswith('GNOME') else f'{x+w//2},{y+h//2}'
   sys.argv=['trial','--cli',str(P/'cli'),'--rect','240,200,1440,820','--stop',stop,'--log',str(P/'helper.log'),'--rel','--label',f'{typ}-{i+1}','--start','2' if typ=='fixed' else '1','--jitter','0' if typ=='fixed' else '5']
   health_before=gnome_health(f"{typ}-{i+1}-before")
   trial.main()
   health_after=gnome_health(f"{typ}-{i+1}-after")
   if health_before!=health_after:raise RuntimeError("GNOME Shell changed during the trial")
if __name__=='__main__':
 flags=list(sys.argv)
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 try:
  L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
  sid=A.rpc('scroll.prepare',{'rect':[240,200,1440,820]})['id'];A.rpc('scroll.start',{'id':sid});time.sleep(1);A.rpc('scroll.cancel',{'id':sid})
  if "--extras-only" not in flags:run(b)
  if "--only-pointer" in flags:sys.exit(0)
  subprocess.run([sys.executable,str(P/'race.py')],check=True)
  for driver in ['user','putgd']:
   b.js('window.scrollTo({top:0,behavior:"instant"}); return 0;');time.sleep(.5)
   sid=A.rpc('scroll.prepare',{'rect':[0,0,1920,1080]})['id'];A.rpc('scroll.start',{'id':sid});time.sleep(.5);A.rpc('scroll.cancel',{'id':sid})
   import re
   m=list(re.finditer(r'scroll: bar at .*cancel (-?\d+),(-?\d+) (\d+)x(\d+)',(P/'helper.log').read_text()))[-1]
   x,y,w,h=map(int,m.groups())
   if A.E.get('XDG_CURRENT_DESKTOP','').upper().endswith('GNOME'):
    text=(P/'helper.log').read_text();q=list(re.finditer(r'scroll: bar at (-?\d+),(-?\d+) (\d+)x(\d+)',text))[-1];sh=list(re.finditer(r'the Shell put the bar at (-?\d+),(-?\d+) (\d+)x(\d+)',text))[-1];x+=int(sh[1])-int(q[1]);y+=int(sh[2])-int(q[2])
   sys.argv=['trial','--cli',str(P/'cli'),'--rect','0,0,1920,1080','--stop',f'{x+w//2},{y+h//2}','--driver',driver,'--log',str(P/'helper.log'),'--rel','--label','inside-cancel-'+driver,'--start','2']
   health_before=gnome_health(f"inside-cancel-{driver}-before")
   trial.main()
   health_after=gnome_health(f"inside-cancel-{driver}-after")
   if health_before!=health_after:raise RuntimeError("GNOME Shell changed during the trial")
 finally:L.browser_stop()
