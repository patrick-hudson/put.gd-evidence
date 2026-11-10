from pathlib import Path
import os,json,shutil
E=Path.home()/'work/i1363/work/acceptance-1363/ap6'
owned=['/tmp/ap6-drive.py','/tmp/ap6-compose.py','/tmp/ap6-annotate.py','/tmp/ap6-export.py','/tmp/ap6-retire.py','/tmp/ap6-launch.log','/tmp/ap6-install.log','/tmp/ap6-install2.log','/tmp/ap6-start.log']
left=[]
for p in Path('/proc').iterdir():
 if p.name.isdecimal():
  try:
   args=(p/'cmdline').read_bytes().decode().split('\0')
   if any(a in owned for a in args):left.append({'pid':int(p.name),'executable':args[0]})
  except (OSError,UnicodeError):pass
for n in owned:
 p=Path(n)
 if p.is_file():shutil.copy2(p,E/('scratch-'+p.name));p.unlink()
r=Path('/tmp/ap6-checks')
if r.is_dir():
 for p in sorted(r.rglob('*'),key=lambda x:len(x.parts),reverse=True):
  if p.is_file():p.unlink()
  elif p.is_dir():p.rmdir()
 r.rmdir()
report={'ownedProcessesRemaining':left,'qemuPidAbsent':not Path('/proc/2265157').exists(),'overlayAbsent':not (Path.home()/'work/i1363/work/lab-runs/ap6/disk.qcow2').exists()}
(E/'final-sweep.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
