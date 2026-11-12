from pathlib import Path
import sys,json,shlex
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
lab.overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd');P=Path('/home/patrick/work/s3a');r=Path('/home/patrick/work/put.gd/work/lab-runs/s3n')
print(lab.ssh(r,'sudo -n apt-get install -y python3-pyqt6 python3-gi python3-gi-cairo gir1.2-gtk-4.0 python3-numpy python3-pil python3-pyatspi fonts-dejavu-core',timeout=400)[-1000:],flush=True)
print(lab.ssh(r,'umask 077; mkdir -p /home/lab/work/s3a',timeout=30),flush=True)
lab.put(r,P/'guest-neon-drivers.tar','/home/lab/work/guest-drivers.tar');print(lab.ssh(r,'tar -xf /home/lab/work/guest-drivers.tar -C /home/lab/work/s3a',timeout=30))
deb=P/'putgd_26.1112.4716~dev+g0311647141ff_amd64.deb'
assert lab.hash_file(deb)=='6ebe37cd7aa5e27d50b31d1d5db15b468135bf381fb710471dc2fd90910181d0'
# The explicit selector-less DEB row intentionally tests the native package on an AppImage profile.
receipt=lab.install_package(r,deb);(P/'neon-native-install.json').write_text(json.dumps(receipt,indent=2));lab.put(r,P/'c16.py','/home/lab/work/s3a/c16.py')
print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 c16.py',timeout=180),flush=True)
print(lab.ssh(r,'sudo -n apt-get remove -y putgd',timeout=180)[-1000:],flush=True)
img=next(P.glob('*.AppImage'));receipt=lab.install_appimage(r,img);(r/'package.json').write_text(json.dumps(receipt,indent=2));(P/'neon-appimage-install.json').write_text(json.dumps(receipt,indent=2))
print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 -c "import pass2; pass2.setup()"',timeout=90),flush=True)
print('READY_APPIMAGE',flush=True)
