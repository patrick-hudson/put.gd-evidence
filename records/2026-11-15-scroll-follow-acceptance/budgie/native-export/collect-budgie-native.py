"""Export owned guest evidence before retiring its disposable overlay."""
import json,hashlib,tarfile,gzip,shutil,subprocess,struct
from pathlib import Path
P=Path.home()/'work/sfa15';files={}
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for root in [P,P/'b']:
 if not root.exists():continue
 for f in root.rglob('*'):
  rel=f.relative_to(root);parts=rel.parts
  if not f.is_file()or f.is_symlink():continue
  if any(x.startswith('profile-')or x in ['squashfs-root','tools','c','d','s','cache','r','__pycache__']for x in parts):continue
  if f.name in ['session-env.json','helper.log']or 'env'==f.stem:continue
  if parts[0]=='b'and root==P:continue
  if f.suffix in ['.py','.json','.jsonl','.png','.log','.err','.md','.html','.xml','.txt','.c','.h']or f.name=='cli':files[str(f.relative_to(P))]=f
 if(root/'helper.log').exists():
  with(root/'helper.log').open('rb')as src,gzip.open(root/'helper-complete.log.gz','wb')as dst:shutil.copyfileobj(src,dst)
  files[str((root/'helper-complete.log.gz').relative_to(P))]=root/'helper-complete.log.gz'
 notice=[]
 for f in(root/'s').rglob('*.jsonl'):
  for line in f.read_text(errors='replace').splitlines():
   if 'scroll_blank_stretch'in line:notice.append(json.loads(line))
 n=root/'blank-notice-log.json';n.write_text(json.dumps(notice,indent=1));files[str(n.relative_to(P))]=n
 proof={'osRelease':Path('/etc/os-release').read_text(),'candidateAppImageSha256':sha(P/'candidate.AppImage'),'nightlyAppImageSha256':sha(P/'nightly.AppImage')if(P/'nightly.AppImage').exists()else None,'binaries':{x:sha(root/'squashfs-root/usr/bin'/x)for x in ['putgd','putgd-cli','putgd-record']},'runtimeRoot':str(root),'pointerObserverSha256':sha(P/'pointer-observer')if(P/'pointer-observer').exists()else None,'systemFirefoxSha256':sha(Path('/usr/lib64/firefox/firefox'))if Path('/usr/lib64/firefox/firefox').exists()else None}
 proof['packages']=subprocess.run(['pacman','-Q','hyprland','omarchy','firefox'],capture_output=True,text=True).stdout if shutil.which('pacman')else subprocess.run(['rpm','-q','labwc','budgie-desktop','firefox'],capture_output=True,text=True).stdout
 n=root/'native-package-proof.json';n.write_text(json.dumps(proof,indent=1));files[str(n.relative_to(P))]=n
index={n:{'sha256':sha(f),'bytes':f.stat().st_size}for n,f in files.items()}
n=P/'native-restore-index.json';n.write_text(json.dumps({'files':index,'note':'All owned native test sources, logs, state pictures and admitted images exported before overlay retirement. Browser profiles, session environment, keys, configuration, caches and vendor/runtime binaries excluded.'},indent=1));files[n.name]=n
out=P/'native-evidence.tar.gz'
with tarfile.open(out,'w:gz')as t:
 for n,f in sorted(files.items()):t.add(f,arcname=n,recursive=False)
print(json.dumps({'path':str(out),'files':len(files),'bytes':out.stat().st_size,'sha256':sha(out)}),flush=True)
