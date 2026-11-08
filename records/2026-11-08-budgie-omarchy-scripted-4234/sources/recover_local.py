import sys,importlib.util,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
spec=importlib.util.spec_from_file_location('sp','work/sp/pass.py');m=importlib.util.module_from_spec(spec);sys.modules['sp']=m;spec.loader.exec_module(m)
run=Path(sys.argv[1]).resolve()
from tools.lab import lab
raw=lab.ssh(run,'find /dev/shm -maxdepth 1 -type d -name "s???????" -printf "%p\\n"')
for root in raw.splitlines():
 t=m.NativeTarget(run=run,session_root=root);native=t.session('printf "%s" "$XDG_RUNTIME_DIR"').strip();t.socket=native+'/putgd/session.sock';t._created_root=True;t._owns_root=True
 left=lab.ssh(run,'test -S '+t.socket+' && echo live || true').strip()
 if left:t.started=True
 print(root,t.close())
