import os,subprocess,time
from pathlib import Path
P=Path('/tmp/v2');real=os.environ['XDG_RUNTIME_DIR'];env=dict(os.environ,WAYLAND_DISPLAY=str(Path(real)/os.environ['WAYLAND_DISPLAY']),PIPEWIRE_RUNTIME_DIR=real,PUTGD_RECORD_DEBUG_LOG=str(P/'helper.log'))
assert len(str(P/'runtime/putgd/session.sock').encode())<=107
for k,n in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_STATE_HOME','state'),('XDG_CACHE_HOME','cache'),('XDG_RUNTIME_DIR','runtime')]:env[k]=str(P/n)
p=subprocess.Popen([str(Path.home()/'putgd-lab/bin/putgd-launcher'),'--background'],env=env,stdout=(P/'resident-restart2.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);print(p.pid);time.sleep(3)
