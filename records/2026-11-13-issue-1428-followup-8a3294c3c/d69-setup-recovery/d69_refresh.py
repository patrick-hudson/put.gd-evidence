from pathlib import Path
import sys,subprocess,json,hashlib
sys.path.insert(0,str(Path.home()/'work/b1428/measure'))
from text_proof import session_environment
e,leader=session_environment(['plasmashell','kwin_wayland']);r=Path.home()/'work/b1428'
p=subprocess.run(['kbuildsycoca6','--noincremental'],env=e,capture_output=True,text=True)
print(json.dumps({'leader':leader,'session':{k:e.get(k) for k in ['XDG_SESSION_TYPE','XDG_RUNTIME_DIR','WAYLAND_DISPLAY','XDG_DATA_HOME','XDG_CACHE_HOME']},'refreshCode':p.returncode,'refreshLog':p.stdout+p.stderr,'desktopEntry':Path('/usr/share/applications/putgd.desktop').read_text(),'binary':str(Path('/usr/bin/putgd').resolve()),'binarySha256':hashlib.sha256(Path('/usr/bin/putgd').read_bytes()).hexdigest()},indent=2));assert p.returncode==0
