import sys,json,subprocess,time,shlex,os,fcntl,tempfile
from pathlib import Path
from importlib.machinery import SourceFileLoader
c=SourceFileLoader('c','/tmp/p1363-campaign.py').load_module()
D=sys.argv[1];h,r,p,g,pin,port,vnc,k,known,wall=c.PROFILES[D];key='/home/patrick/work/put.gd/work/lab-bootstrap-'+k+'/identity'
P=c.OUT/'packages-13570fca9';pattern={'cinnamon':('release-native-ubuntu24.04','*.deb'),'gnome':('release-native-ubuntu26.04','*.deb'),'kde':('release-native-ubuntu26.04','*.deb'),'budgie':('release-appimage','*.AppImage'),'hyprland':('release-native-archlinux','*.pkg.tar.zst')}[D]
if '--appimage' in sys.argv:pattern=('release-appimage','*.AppImage')
if '--rpm' in sys.argv:pattern=('release-native-fedora44','*.rpm')
files=list((P/pattern[0]).glob(pattern[1]));assert len(files)==1,files
pkg=files[0];remote_pkg='/home/patrick/work/i1363/work/acceptance-packages-13570fca9/'+pattern[0]+'/'+pkg.name
c.remote(h,'mkdir -p '+shlex.quote(str(Path(remote_pkg).parent)))
for source,destination in [(pkg,remote_pkg),(Path('/tmp/p1363-base-run.py'),'/tmp/p1363-base-run.py'),(Path('/tmp/p1363-observe-budgie.py'),'/tmp/p1363-observe-budgie.py'),(Path('/tmp/p1363-checks-recorded.py'),'/tmp/p1363-checks.py'),(Path('/tmp/p1363-mcp-live.py'),'/tmp/p1363-mcp-live.py')]:subprocess.run(['rsync','-q','-e',' '.join(c.ssh(h)[:-1]),str(source),c.ssh(h)[-1]+':'+destination],check=True)
c.launch(D)
try:
 c.remote(h,('P1363_GUI=after ' if '--gui-after' in sys.argv else 'P1363_GUI=1 ' if '--gui' in sys.argv else '')+shlex.join(['python3','/tmp/p1363-base-run.py',D,r,key,remote_pkg]))
finally:
 # Preserve evidence before the overlay can be retired. Failed runs remain stopped for investigation.
 target=c.OUT/'base'/D/r;target.mkdir(parents=True,exist_ok=True)
 subprocess.run(['rsync','-r','-e',' '.join(c.ssh(h)[:-1]),c.ssh(h)[-1]+':/home/patrick/work/i1363/work/acceptance-1363/'+r+'/',str(target)+'/'],check=True)
 unit='putgd-vm-1363acc-'+r
 subprocess.run(['systemctl','--user','stop',unit],check=False)
 path=Path('/home/patrick/work/put.gd/tools/qemu-grid/remote-displays.json')
 with open('/tmp/p1363-wall.lock','w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);rows=json.loads(path.read_text());rows=[row for row in rows if row.get('group')!='1363acc-'+r]
  fd,tmp=tempfile.mkstemp(dir=path.parent);os.write(fd,(json.dumps(rows,indent=1)+'\n').encode());os.close(fd);os.chmod(tmp,0o664);os.replace(tmp,path)
print('EVIDENCE',target,flush=True)
