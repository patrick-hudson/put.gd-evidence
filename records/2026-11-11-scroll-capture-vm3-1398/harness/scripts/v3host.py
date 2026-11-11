import sys,json,time,subprocess,shlex,concurrent.futures,traceback,os
from pathlib import Path
from PIL import Image
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
mode,keys=sys.argv[1:3]
def go(k):
 r=B/'repo/work/lab-runs'/(k+'3');o=B/'v3evidence'/k;o.mkdir(exist_ok=True)
 def cmd(c,timeout=300):return lab.guest_session(r,c,timeout=timeout)
 def shot(n):Image.open(lab.screenshot(r,'v3-'+n)['path']).save(o/(n+'.png'))
 def spawn(c,n):return int(cmd('nohup '+c+' > /tmp/v3/'+n+'.log 2>&1 < /dev/null & echo $!').strip())
 def case(n,rect='0,0,1280,800'):
  if k=='o' and n!='postcap':time.sleep(7)
  print(k,n,'START',flush=True);(o/(n+'.console')).write_text(cmd('python3 /home/lab/v3guest.py case '+n+' '+rect));shot(n+'-end');print(k,n,'END',flush=True)
 try:
  if mode=='prepare':
   deps={'o':'pacman -Sy --noconfirm python-gobject gtk4 python-pyqt6 python-pillow python-numpy','b':'dnf install -y python3-gobject gtk4 python3-pyqt6-base python3-pillow python3-numpy','n':'apt-get update && sudo -n apt-get install -y python3-gi gir1.2-gtk-4.0 python3-pyqt6 python3-pil python3-numpy','k':'apt-get update && sudo -n apt-get install -y python3-gi gir1.2-gtk-4.0 python3-pyqt6 python3-pil python3-numpy'}[k]
   (o/'dependencies.log').write_text(lab.ssh(r,'sudo -n '+deps,timeout=500))
   (o/'install.json').write_text(json.dumps(lab.install(r,appimage=B/'ci3.AppImage'),indent=2))
   for source,target in [(B/'v3guest.py','v3guest.py'),(B/'v3text.py','v3text.py'),(B/'v2receiver.py','v3receiver.py'),(B/'v2ruler.html','v3ruler.html'),(Path('/home/patrick/work/sf1398/qt_fixture.py'),'v3ruler.py')]:
    if target=='v3receiver.py':
     f=B/'v3receiver.py';f.write_text(source.read_text().replace('/tmp/v2','/tmp/v3'));source=f
    lab.put(r,source,'/home/lab/'+target)
   (o/'init.log').write_text(cmd('python3 /home/lab/v3guest.py init'))
   (o/'identity.log').write_text(cmd('cat /etc/os-release; loginctl list-sessions; (kwin_wayland --version || labwc --version || hyprctl version) 2>/dev/null'))
   shot('desktop-ready');print(k,'PREPARED',flush=True)
  elif mode=='browser':
   cmd('mkdir -p /home/lab/v3firefox');prefs='user_pref("browser.shell.checkDefaultBrowser", false); user_pref("browser.aboutwelcome.enabled", false); user_pref("browser.startup.homepage_override.mstone", "ignore"); user_pref("browser.newtabpage.activity-stream.asrouter.userprefs.cfr.addons", false);'
   cmd('printf %s '+shlex.quote(prefs)+' > /home/lab/v3firefox/user.js')
   browser='chromium --no-first-run --password-store=basic --user-data-dir=/tmp/v3/chromium --kiosk file:///home/lab/v3ruler.html' if k=='o' else 'firefox --no-remote --profile /home/lab/v3firefox --kiosk file:///home/lab/v3ruler.html'
   pid=spawn(browser,'browser');(o/'browser.pid').write_text(str(pid));time.sleep(18);shot('browser-ready')
  elif mode=='repeat':
   for i in range(1,21 if k in 'nk' else 6):case('clean%02d'%i)
  elif mode=='text':
   cmd('kill '+(o/'browser.pid').read_text());time.sleep(2)
   for kind in ['gtk','qt']:
    for width in [1280,600]:
     name=kind+str(width);pid=spawn('python3 /home/lab/v3text.py '+kind+' '+str(width),name);time.sleep(4);shot(name+'-ready')
     for i in range(1,4):case(name+'-'+str(i),'0,100,'+str(width-20)+',600')
     cmd('kill '+str(pid));time.sleep(1)
  elif mode=='extras':
   for name,start in [('long'+str(i),0) for i in range(1,6 if k=='b' else 2)]+[('half-on',12000),('half-off',12000),('stop-top',12000),('stop-mid',0),('cancel',0),('cap',0),('postcap',0)]:
    
    old=o/(name+'.console')
    if old.exists():
     try:
      prior=json.loads(old.read_text())
      if prior.get('capture',{}).get('state')=='done' and not prior.get('error'):continue
     except Exception:pass
    pid=spawn('env SC_Y=100 python3 /home/lab/v3ruler.py --rows 600 --start '+str(start),name);time.sleep(3);shot(name+'-ready');case(name,'100,100,960,600');cmd('kill '+str(pid));time.sleep(1)
  elif mode=='export':
   code="""import tarfile,json,hashlib
from pathlib import Path
p=Path('/tmp/v3');files=[]
for n in ['cases','received','archive']:
 files += [f for f in (p/n).rglob('*') if f.is_file()]
files += [f for f in p.iterdir() if f.is_file() and (f.suffix in ['.log','.json','.jsonl'])]
with tarfile.open('/home/lab/v3-export.tgz','w:gz') as t:
 for f in files:t.add(f,arcname=str(f.relative_to(p)))
print(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}))
"""
   (o/'hashes.json').write_text(cmd('python3 -c '+shlex.quote(code)));lab.get(r,'/home/lab/v3-export.tgz',o/'export.tgz');import tarfile,hashlib
   (o/'final').mkdir(exist_ok=True);tarfile.open(o/'export.tgz').extractall(o/'final',filter='data');assert all(hashlib.sha256((o/'final'/n).read_bytes()).hexdigest()==h for n,h in json.loads((o/'hashes.json').read_text()).items());(o/'state.json').write_text((r/'state.json').read_text());print(k,'EXPORTED VERIFIED',flush=True)
 except Exception: (o/(mode+'-error.txt')).write_text(traceback.format_exc());print(k,traceback.format_exc(),flush=True)
with concurrent.futures.ThreadPoolExecutor(2) as p:list(p.map(go,keys))
