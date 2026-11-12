from pathlib import Path
import subprocess,json,os,shutil
P=Path('/home/patrick/work/s3a');entry=Path.home()/'.config/autostart/putgd.desktop';backup=P/'autostart-original-private';entry.parent.mkdir(parents=True,exist_ok=True)
meta={'entry':str(entry),'existed':entry.exists() or entry.is_symlink(),'backupPrivate':str(backup)}
if meta['existed']:os.replace(entry,backup)
entry.write_text('[Desktop Entry]\nType=Application\nName=put.gd lab autostart guard\nHidden=true\n');entry.chmod(0o600);(P/'autostart-guard.json').write_text(json.dumps(meta,indent=2))
subprocess.run(['python3',str(P/'install-native.py'),'f44',str(P/'putgd-26.1112.4660-nightly-fedora44-x86_64.rpm')],check=True)
shutil.copyfile(P/'installed.json',P/'nightly-installed.json')
with (P/'test-dependencies-install.log').open('w') as log:r=subprocess.run(['sudo','-n','dnf','install','-y','dejavu-sans-mono-fonts','chromium'],stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0,r.returncode
(P/'packages-after.txt').write_bytes(subprocess.check_output(['rpm','-qa','--qf','%{NAME}\n']))
print('nightly and distro test dependencies installed',flush=True)
