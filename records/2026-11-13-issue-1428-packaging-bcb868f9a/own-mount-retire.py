import datetime,json,os,signal,subprocess,time
from pathlib import Path
r=Path.home()/'work/ocr-integration-bcb-artifacts'
p=Path('/proc/999934'); expected=str(r/'integration-appimage/putgd-26.1113.4805-dev+gbcb868f9ac5b-x86_64.AppImage')
assert p.stat().st_uid==os.getuid()
assert (p/'cmdline').read_bytes().split(b'\0')[:2]==[expected.encode(),b'--appimage-mount']
assert (p/'stat').read_text().split(') ',1)[1].split()[19]=='123440017'
os.kill(999934,signal.SIGINT)
mount=Path('/tmp/.mount_putgd-fGkdkk');deadline=time.monotonic()+5
while mount.is_mount() and time.monotonic()<deadline:time.sleep(.05)
if mount.is_mount():subprocess.run(['/usr/bin/fusermount','-u',str(mount)],check=True,timeout=15)
assert not mount.is_mount()
(r/'mount-cleanup-retry.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mount':str(mount),'runtimePid':999934,'runtimeStartTicks':'123440017','command':'SIGINT exact verified owned runtime PID, then wait for FUSE unmount','unmounted':True,'reason':'First cleanup sampled before asynchronous FUSE exit; next attempt unmounted too early while runtime held mount'},indent=2)+'\n')
print('Exact owned runtime retired; FUSE mount gone.')
