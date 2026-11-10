import sys,os,json,subprocess,pathlib
home=pathlib.Path.home();base=home/'work/s1364b' if sys.argv[1]!='guest' else home
sys.path.insert(0,str(base/'lab'))
import record_run as rr
kind=sys.argv[1];rounds=5 if kind=='guest' else 3
if kind=='guest':
 builds=[('nightly',next((home/'apps/nightly').glob('*.AppImage'))),('pr',next((home/'apps/pr').glob('*.AppImage')))]
 an=home/'an';an.mkdir(exist_ok=True);subprocess.run([str(builds[1][1]),'--appimage-extract'],cwd=an,stdout=subprocess.DEVNULL,check=True);an=an/'squashfs-root'
else:
 builds=[(x,base/'roots'/x/'usr/bin') for x in ['nightly','pr']];an=base/'roots/pr'
args=['--run',str(base/'r'),'--analyzer',str(an),'--video','marker','--rounds',str(rounds),'--target','region','--rect','0,0,960,540','--format','mp4','webm','--lead','6','--pause-for','0','--pause-at','14','--after','2','--mic','off','--system','tone','--no-notifications','--keep-unpaired','--min-pairs','10','--frames']
for name,p in builds:args+=['--build',name+'='+str(p)]
if kind=='guest':args+=['--vnc-port','0','--video-size','640x360']
if kind=='gnome':args+=['--vnc-port','5901']
# Same existing fullscreen guard for every Hyprland target; preserve coverage checks.
source=(base/'lab/record_run.py').read_text().replace("if a.target == 'window' and self.env.get('HYPRLAND_INSTANCE_SIGNATURE'):","if self.env.get('HYPRLAND_INSTANCE_SIGNATURE'):")
source=source.replace("if __name__ == '__main__':","if False:")
exec(compile(source,str(base/'lab/record_run.py'),'exec'),rr.__dict__)
original=rr.Driver.start_resident
backups={}
if kind=='plasma':
 def start(self,build):
  active=base/'active'
  subprocess.run(['rsync','-rlpc',str(build.path.parent.parent)+'/',str(active)+'/'],check=True)
  activebin=active/'usr/bin'
  build.launcher=[str(activebin/'putgd'),'--background'];build.cli=str(activebin/'putgd-cli')
  entrydir=home/'.local/share/applications';entrydir.mkdir(parents=True,exist_ok=True)
  for name,exe in [('putgd.desktop','putgd'),('putgd-record.desktop','putgd-record')]:
   p=entrydir/name
   if p not in backups:backups[p]=(p.read_bytes(),p.stat().st_mode&0o777) if p.exists() else None
   text='[Desktop Entry]\nType=Application\nName=put.gd timing lab\nExec='+str(activebin/exe)+'\nNoDisplay=true\nX-KDE-DBUS-Restricted-Interfaces=org.kde.KWin.ScreenShot2\nX-KDE-Wayland-Interfaces=zkde_screencast_unstable_v1\n'
   p.write_text(text);private=self.run/'data/applications'/name;private.parent.mkdir(parents=True,exist_ok=True);private.write_text(text)
  subprocess.run(['kbuildsycoca6','--noincremental'],env=self.env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
  return original(self,build)
 rr.Driver.start_resident=start
try:rc=rr.main(args)
finally:
 for p,saved in backups.items():
  if saved is None:p.unlink(missing_ok=True)
  else:p.write_bytes(saved[0]);p.chmod(saved[1])
 if backups:subprocess.run(['kbuildsycoca6','--noincremental'],env=rr.session_environment()[0],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
(base/'done').write_text(str(rc)+'\n');sys.exit(rc)
