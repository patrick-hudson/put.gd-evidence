from pathlib import Path
from trial import cli
import os,signal,json,sys,subprocess
l=Path.home()/'work/s5302';a=l/'a';phase=sys.argv[1];sid=(a/'terminal-session-id').read_text();v=cli(str(l/'bin/cli-a'),'scroll.cancel',{'id':sid});(a/(phase+'-cancel.json')).write_text(json.dumps(v,indent=2));assert v['ok'],v
pid=int((a/'terminal.pid').read_text());cmd=Path(f'/proc/{pid}/cmdline').read_bytes();assert b'foot' in cmd and b'terminal-witness.py' in cmd;os.kill(pid,signal.SIGTERM)
print(phase,'cancelled and own terminal closed',pid)
