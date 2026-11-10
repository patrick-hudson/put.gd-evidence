import os,json,subprocess,sys
from pathlib import Path
p=Path('/tmp/sp1398');env=json.loads((p/'env.json').read_text());kind=sys.argv[1]
cmd=['python3',str(p/'scroll_run.py'),'--socket',str(p/'runtime/putgd/session.sock'),'--out',str(p/kind),'--package',str(next(p.glob('*.deb'),next(p.glob('*.rpm'),None))),'--rect','100,100,960,600','--rows','60','--format','fixture','--png-root',str(p/'archive'),'--png-root',str(p/'data'),'--open','firefox --no-remote --profile /tmp/sp1398/firefox --kiosk','--page',str(p/'ruler.html')]
if kind.startswith('cap'):cmd+=['--max-height','2000','--height','2000','--expect-end','height_cap']
if kind.startswith('stop'):cmd+=['--control','stop','--after','3','--expect-end','stopped']
if kind.startswith('cancel'):cmd+=['--control','cancel','--after','2']
if kind.startswith('qt'):
 i=cmd.index('--open');cmd=cmd[:i]
(p/'firefox').mkdir(exist_ok=True)
subprocess.run(cmd,env=env)
