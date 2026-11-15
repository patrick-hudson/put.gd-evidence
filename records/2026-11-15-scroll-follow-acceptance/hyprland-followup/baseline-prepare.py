import os,hashlib,subprocess,shutil
from pathlib import Path
P=Path.home()/'work/sfa15';B=P/'b'
assert hashlib.sha256((P/'nightly.AppImage').read_bytes()).hexdigest()=='0b60880785851dee4febd216998dc0d2d00bfada167d7cc366eb7c254b198695'
assert not B.exists();B.mkdir(mode=0o700)
assert len(str((B/'r/putgd/session.sock').resolve()).encode())<=107
for n in ['r','tools']:(B/n).mkdir(mode=0o700)
for n in ['firefox','chrome-linux64']:
 if (P/'tools'/n).exists():(B/'tools'/n).symlink_to(P/'tools'/n)
os.chmod(P/'nightly.AppImage',0o700)
with (B/'extract.log').open('w') as f:subprocess.run([str(P/'nightly.AppImage'),'--appimage-extract'],cwd=B,stdout=f,check=True)
s=(P/'cli').read_text().replace(str(P/'squashfs-root'),str(B/'squashfs-root')).replace(str(P/'r/putgd/session.sock'),str(B/'r/putgd/session.sock'));(B/'cli').write_text(s);os.chmod(B/'cli',0o700)
print('baseline AppImage SHA256',hashlib.sha256((P/'nightly.AppImage').read_bytes()).hexdigest(),'socketBytes',len(str((B/'r/putgd/session.sock').resolve()).encode()),flush=True)
