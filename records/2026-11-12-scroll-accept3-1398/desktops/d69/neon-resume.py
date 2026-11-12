from pathlib import Path
import sys,json
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
lab.overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd');P=Path('/home/patrick/work/s3a');r=Path('/home/patrick/work/put.gd/work/lab-runs/s3n')
print(lab.ssh(r,'mv /home/lab/work/s3a/c16 /home/lab/work/s3a/c16-attempt2; cp /home/lab/work/s3a/c16.py /home/lab/work/s3a/c16-attempt2/source.py',timeout=30))
lab.put(r,P/'c16.py','/home/lab/work/s3a/c16.py')
cmd='cd /home/lab/work/s3a && set +e; python3 c16.py > c16.console 2>&1; code=$?; cat c16.console; echo C16_EXIT:$code'
print(lab.guest_session(r,cmd,timeout=180),flush=True)
print(lab.ssh(r,'sudo -n apt-get remove -y putgd',timeout=180)[-1000:],flush=True)
img=next(P.glob('*.AppImage'));receipt=lab.install_appimage(r,img);(r/'package.json').write_text(json.dumps(receipt,indent=2));(P/'neon-appimage-install.json').write_text(json.dumps(receipt,indent=2))
lab.put(r,P/'guest-late-fixture-current.py','/home/lab/work/s3a/late_fixture.py')
print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 -c "import pass2; pass2.setup()"',timeout=90),flush=True)
print('READY_APPIMAGE',flush=True)
