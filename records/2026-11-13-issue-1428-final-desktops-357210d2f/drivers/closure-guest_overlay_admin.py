# Run as root only inside: unshare --mount --propagation private python3 ... NAME
from pathlib import Path
import sys,subprocess,os,json,time
name=sys.argv[1];assert name.isalnum() and name.startswith('f');root=Path('/home/patrick/work/b1428/r/work/lab-runs');run=root/name;disk=run/'disk.qcow2';assert disk.is_file() and not disk.is_symlink() and disk.parent==run
state=json.loads((run/'state.json').read_text());assert Path(state['overlay'])==disk
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  c=(p/'cmdline').read_bytes().split(b'\0')
  if c and Path(c[0].decode()).name.startswith('qemu-system'):assert not any(str(disk).encode() in x for x in c),'Overlay is running'
 except (FileNotFoundError,ProcessLookupError):pass
subprocess.run(['modprobe','nbd','max_part=16'],check=True);nb=Path('/sys/block/nbd0/pid');assert not nb.exists() or not nb.read_text().strip(),'nbd0 already in use'
m=Path('/run/b1428-'+name);m.mkdir(mode=0o700);mounted=False;connected=False;selected=None
try:
 subprocess.run(['qemu-nbd','--connect','/dev/nbd0','--format','qcow2',str(disk)],check=True);connected=True;subprocess.run(['udevadm','settle'],check=True)
 rows=json.loads(subprocess.check_output(['lsblk','-J','-p','-o','NAME,FSTYPE','/dev/nbd0']))['blockdevices'][0].get('children',[])
 for row in rows:
  fs=row.get('fstype')
  if fs not in ('ext4','btrfs'):continue
  opts=['ro'] if fs=='ext4' else ['ro,subvol=root','ro,subvol=@','ro']
  for opt in opts:
   v=subprocess.run(['mount','-o',opt,row['name'],str(m)],capture_output=True,text=True)
   if v.returncode:continue
   mounted=True
   if (m/'etc/os-release').is_file() and (m/'etc/passwd').is_file() and any(x.startswith('lab:') for x in (m/'etc/passwd').read_text().splitlines()):selected=(row['name'],opt.replace('ro','rw',1));break
   subprocess.run(['umount',str(m)],check=True);mounted=False
  if selected:break
 assert selected,'Guest root partition not found'
 subprocess.run(['umount',str(m)],check=True);mounted=False
 subprocess.run(['mount','-o',selected[1],selected[0],str(m)],check=True);mounted=True
 p=m/'etc/sudoers.d/99-b1428-lab';assert not p.exists();p.write_text('lab ALL=(ALL) NOPASSWD: ALL\n');p.chmod(0o440)
 if (m/'etc/selinux/targeted/contexts/files/file_contexts').is_file():subprocess.run(['chcon','--reference='+str(m/'etc/sudoers'),str(p)],check=True)
 subprocess.run(['visudo','-cf',str(p)],check=True);subprocess.run(['sync','-f',str(p)],check=True)
 print(json.dumps({'run':str(run),'overlay':str(disk),'scope':'Stopped disposable overlay only; golden never mounted or modified','write':'/etc/sudoers.d/99-b1428-lab','mode':'0440','purpose':'Distribution package dependencies and kernel helper exit observer','rootPartition':selected[0]}))
finally:
 if mounted:subprocess.run(['umount',str(m)],check=True)
 if connected:subprocess.run(['qemu-nbd','--disconnect','/dev/nbd0'],check=True)
 m.rmdir()
