from pathlib import Path
import json,subprocess,os
r=Path.home()/'work/b1428';names=['kx','gx','gw','bk','hk','fg','fkx','fgx','fgw','fbk','fhk'];rows=[]
for n in names:
 run=r/'r/work/lab-runs'/n
 if not run.exists():continue
 st=json.loads((run/'state.json').read_text());disk=Path(st['overlay']);assert disk.parent==run;assert not disk.exists(),str(disk)
 rows.append({'name':n,'id':st['id'],'golden':st['golden'],'goldenSha256':st['golden_sha256'],'overlayExists':disk.exists(),'stateRetained':True,'cleanupReceipts':[x.name for x in run.iterdir() if any(w in x.name for w in ['retir','cleanup'])]})
processes=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  args=(proc/'cmdline').read_bytes().split(b'\0');exe=Path(args[0].decode()).name if args and args[0] else ''
  if exe.startswith('qemu-system') and any(str(r/'r/work/lab-runs').encode() in x for x in args):processes.append(int(proc.name))
 except (FileNotFoundError,ProcessLookupError,PermissionError):pass
assert not processes
nbd=Path('/sys/block/nbd0/pid');assert not nbd.exists() or not nbd.read_text().strip()
p=subprocess.run(['rpm','-q','putgd'],capture_output=True,text=True);assert p.returncode==1
print(json.dumps({'allListedOverlaysRetired':True,'runs':rows,'ownQemuPids':processes,'nbd0Disconnected':True,'physicalPutgdPackageInstalled':False,'physicalUserGnomeExtensionExists':(Path.home()/'.local/share/gnome-shell/extensions/putgd@put.gd').exists(),'physicalSystemGnomeExtensionExists':Path('/usr/share/gnome-shell/extensions/putgd@put.gd').exists()},indent=2))
