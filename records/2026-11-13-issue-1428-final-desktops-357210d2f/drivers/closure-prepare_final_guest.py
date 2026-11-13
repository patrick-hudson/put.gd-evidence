from pathlib import Path
import sys,subprocess,shlex,tarfile,hashlib,json
host=Path.home()/'work/b1428';name,kind,target=sys.argv[1:];assert kind in ('native','ai');assert target in ('ubuntu24','ubuntu26','none');g=host/'guest.py';f=host/'final'
def guest(*a):subprocess.run(['python3',str(g),name,*a],check=True)
guest('python3 -c '+shlex.quote("from pathlib import Path;p=Path('/home/lab/b1428');p.mkdir(mode=0o700,exist_ok=True);(p/'final').mkdir(mode=0o700)"))
a=f/'guest-driver.tar'
with tarfile.open(a,'w') as t:
 for p in (f/'scenario').iterdir():
  if p.is_file() and p.suffix in ('.py','.png'):t.add(p,arcname=p.name)
guest('--copy',str(a),str(f/'final_run.py'),'/home/lab/b1428/final/')
if kind=='ai':guest('--copy',str(f/'candidate.AppImage'),'/home/lab/b1428/final/')
else:
 pkg=next((f/target).glob('*.deb')) if target=='ubuntu24' else next(f.glob('*.deb'));guest('--copy',str(pkg),'/home/lab/b1428/final/')
code="""from pathlib import Path
import tarfile,hashlib,subprocess,json
r=Path('/home/lab/b1428/final');p=r/'scenario';p.mkdir(mode=0o700)
with tarfile.open(r/'guest-driver.tar') as t:t.extractall(p,filter='data')
a=r/'candidate.AppImage'
if a.exists():
 retained=Path.home()/'work/b1428';retained.mkdir(mode=0o700,parents=True,exist_ok=True);assert retained.stat().st_uid==__import__('os').getuid() and not retained.is_symlink()
 assert hashlib.sha256(a.read_bytes()).hexdigest()=='eaf9bc8fe00e55cf697e7d35ae6e6253c8f7234e2b4a093e4e1c8427ebe7a095';a.chmod(0o700);w=r/'image';w.mkdir();subprocess.run([str(a),'--appimage-extract'],cwd=w,check=True,stdout=subprocess.DEVNULL);lib=w/'squashfs-root/usr/lib';cli=w/'squashfs-root/usr/bin/putgd-cli';s=r/'cli';s.write_text('#!/bin/sh\\nexport LD_LIBRARY_PATH='+str(lib)+':'+str(lib/'putgd')+'\\nexec '+str(cli)+' \"$@\"\\n');s.chmod(0o700)
print(json.dumps({x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in r.iterdir() if x.suffix in ('.AppImage','.deb')}))
"""
guest('python3 -c '+shlex.quote(code))
