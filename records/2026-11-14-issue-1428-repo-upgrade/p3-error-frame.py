import pathlib,os,subprocess,sys,time
out=pathlib.Path.home()/'repo1428p3'
for p in pathlib.Path('/proc').iterdir():
 try:
  if (p/'comm').read_text().strip()=='quickshell':
   e=dict(v.split('=',1) for v in (p/'environ').read_bytes().decode().split('\0') if '=' in v)
   if 'WAYLAND_DISPLAY' in e:break
 except (OSError,UnicodeError):pass
os.environ.update(e)
f=subprocess.Popen(['/usr/bin/foot','--hold','/usr/bin/putgd-cli','--version-json'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 time.sleep(2);sys.path.insert(0,str(out));from rfb import RFB
 c=RFB(5940,host='10.0.2.2');c.screenshot(str(out/'p3-loader-result.png'));c.close()
finally:
 f.terminate();f.wait(timeout=5);print('stopped terminal PID',f.pid)
