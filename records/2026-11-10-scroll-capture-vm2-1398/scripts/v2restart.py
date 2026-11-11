import os,subprocess,json,time
from pathlib import Path
P=Path('/tmp/v2');real=os.environ['XDG_RUNTIME_DIR'];signature=os.environ['HYPRLAND_INSTANCE_SIGNATURE']
paths=[str(Path(real)/'hypr'/signature/n) for n in ['.socket.sock','.socket2.sock']]+[str(P/'runtime/hypr'/signature/n) for n in ['.socket.sock','.socket2.sock']]
assert all(len(s.encode())<=107 for s in paths)
(P/'hypr-socket-preflight.json').write_text(json.dumps({s:len(s.encode()) for s in paths},indent=2))
(P/'runtime/hypr').symlink_to(Path(real)/'hypr',target_is_directory=True)
(P/'cases').rename(P/'harness-no-hypr');(P/'cases').mkdir()
env=dict(os.environ,WAYLAND_DISPLAY=str(Path(real)/os.environ['WAYLAND_DISPLAY']),PIPEWIRE_RUNTIME_DIR=real,PUTGD_RECORD_DEBUG_LOG=str(P/'helper.log'))
for k,n in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_STATE_HOME','state'),('XDG_CACHE_HOME','cache'),('XDG_RUNTIME_DIR','runtime')]:env[k]=str(P/n)
p=subprocess.Popen([str(Path.home()/'putgd-lab/bin/putgd-launcher'),'--background'],env=env,stdout=(P/'resident-restart.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(p.pid)
