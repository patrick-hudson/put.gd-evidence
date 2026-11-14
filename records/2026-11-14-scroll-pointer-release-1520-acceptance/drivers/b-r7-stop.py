from pathlib import Path
import json
from trial import cli
l=Path.home()/'work/s1520';a=l/'a';p=a/'helper.log';text=p.read_bytes()[int((a/'terminal-log-offset').read_text()):].decode();(a/'terminal-quiet.log').write_text(text);print('sent injections',sum('scroll inject:' in s and 'sent' in s for s in text.splitlines()));print('witness',(a/'terminal-received.txt').read_text());v=cli(str(l/'bin/cli-a'),'scroll.stop',{'id':(a/'terminal-session-id').read_text()});(a/'terminal-stop.json').write_text(json.dumps(v,indent=2));print(v)
