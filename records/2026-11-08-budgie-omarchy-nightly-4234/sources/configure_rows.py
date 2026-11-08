import sys,json,datetime
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import nightly_desktops as n
root=Path.cwd();tag=sys.argv[1]
now=datetime.datetime.now(datetime.timezone.utc);cutoff=now.replace(hour=7,minute=0,second=0,microsecond=0)
if cutoff<=now:cutoff+=datetime.timedelta(days=1)
rows=(('r1','np1','f44','ubuntu-budgie-2404','deb','u24-prepare'),('r2','np2','d69','fedora45-budgie','appimage','f45-prepare'),('r3','np3','d69','omarchy-hyprland','arch','arch-prepare'),('r4','np4','d69','fedora44-budgie','rpm','f44-prepare2'),('r5','np5','d69','ubuntu-budgie-2604','deb','u26-prepare'))
for rid,run,host,desktop,package,prep in rows:
 c=dict(tag=tag,host=host,campaignCutoffUtc=cutoff.isoformat(),row=dict(desktop=desktop,profile=desktop,package=package),run=str(root/'work/lab-runs'/run),output=str(root/'work/np'/rid),profiles=str(root/'work/np'/prep/'profiles'),catalog=str(root/'work/np/assets'/tag/'catalog'),identity=str(root/'work/np/assets'/tag/'identity.json'))
 n.save(root/'work/np'/(rid+'-config.json'),c)
