from pathlib import Path
import subprocess,json,os,time
import record_run
P=Path('/home/patrick/work/s3a')
r=subprocess.run(['python3',str(P/'cleanup-native.py'),'f44']);assert r.returncode==0
meta=json.loads((P/'autostart-guard.json').read_text());entry=Path(meta['entry']);assert entry.read_text()=='[Desktop Entry]\nType=Application\nName=put.gd lab autostart guard\nHidden=true\n';entry.unlink()
if meta['existed']:os.replace(meta['backupPrivate'],entry)
e,_=record_run.session_environment()
for key,file in [('enabled-extensions','original-enabled-extensions.txt'),('disabled-extensions','original-disabled-extensions.txt'),('disable-user-extensions','original-disable-user-extensions.txt')]:
 subprocess.run(['gsettings','set','org.gnome.shell',key,(P/file).read_text().strip()],env=e,check=True)
audit=subprocess.run(['python3',str(P/'audit-apps.py')],capture_output=True,text=True);(P/'restore-prelogout-apps.json').write_text(audit.stdout);assert audit.returncode==0,'Patrick app or incomplete inventory; logout refused'
old=subprocess.check_output(['pgrep','-u',str(os.getuid()),'-x','gnome-shell'],text=True).split();subprocess.run(['sudo','-n','systemctl','restart','gdm'],check=True)
for _ in range(60):
 now=subprocess.run(['pgrep','-u',str(os.getuid()),'-x','gnome-shell'],text=True,capture_output=True).stdout.split()
 if now and set(now).isdisjoint(old):break
 time.sleep(1)
else:raise RuntimeError('restored GNOME session unavailable')
time.sleep(8);e,_=record_run.session_environment();subprocess.run(['systemctl','--user','restart','putgd-gnome-vnc.service'],env=e,check=True)
subprocess.run(['gdbus','call','--session','-d','org.gnome.Shell','-o','/org/gnome/Shell','-m','org.freedesktop.DBus.Properties.Set','org.gnome.Shell','OverviewActive','<false>'],env=e,capture_output=True)
restored={}
for key,file in [('enabled-extensions','original-enabled-extensions.txt'),('disabled-extensions','original-disabled-extensions.txt'),('disable-user-extensions','original-disable-user-extensions.txt')]:
 value=subprocess.check_output(['gsettings','get','org.gnome.shell',key],env=e,text=True).strip();restored[key]={'before':(P/file).read_text().strip(),'after':value,'match':value==(P/file).read_text().strip()}
full=subprocess.check_output(['rpm','-qa','--qf','%{NAME} %{VERSION}-%{RELEASE} %{ARCH}\n'],text=True);(P/'package-status-restored.txt').write_text(full);before=set((P/'package-status-before.txt').read_text().splitlines());after=set(full.splitlines())
v={'extensions':restored,'packageVersionsMatch':before==after,'packageVersionsAdded':sorted(after-before),'packageVersionsMissing':sorted(before-after),'autostartRestored':True,'oldShellPids':old,'newShellPids':now}
(P/'restore-final.json').write_text(json.dumps(v,indent=2));print(v,flush=True);assert all(x['match'] for x in restored.values()) and before==after
