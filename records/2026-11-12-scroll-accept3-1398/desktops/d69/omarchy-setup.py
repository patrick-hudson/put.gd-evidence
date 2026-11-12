from pathlib import Path
import sys,json
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
lab.overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd');P=Path('/home/patrick/work/s3a');r=Path('/home/patrick/work/put.gd/work/lab-runs/s3h')
print(lab.ssh(r,'sudo -n /usr/bin/pacman -Sy --noconfirm --needed python-pyqt6 python-gobject gtk4 python-numpy python-pillow ttf-dejavu > /home/lab/accept3-packages-sync.log 2>&1; code=$?; tail -c 2000 /home/lab/accept3-packages-sync.log; exit $code',timeout=400),flush=True)
print(lab.ssh(r,'umask 077; mkdir -p /home/lab/work/s3a',timeout=30))
lab.put(r,P/'guest-omarchy-drivers.tar','/home/lab/work/guest-drivers.tar');print(lab.ssh(r,'tar -xf /home/lab/work/guest-drivers.tar -C /home/lab/work/s3a',timeout=30))
img=next(P.glob('*.AppImage'));receipt=lab.install_appimage(r,img);(r/'package.json').write_text(json.dumps(receipt,indent=2));(P/'omarchy-appimage-install.json').write_text(json.dumps(receipt,indent=2))
print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 -c "import pass2; pass2.setup()"',timeout=90),flush=True)
print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 guest-native-suite.py',timeout=7200),flush=True)
