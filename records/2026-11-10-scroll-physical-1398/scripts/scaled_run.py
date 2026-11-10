import json,subprocess,time
from pathlib import Path
p=Path('/tmp/sp1398');e=json.loads((p/'env.json').read_text());time.sleep(3)
subprocess.run(['python3',str(p/'scroll_run.py'),'--socket',str(p/'runtime/putgd/session.sock'),'--out',str(p/'qt-fractional150'),'--package',str(p/'putgd_26.1110.4635~dev+ge3c1bd6b840a_amd64.deb'),'--rect','200,200,1920,1200','--rows','60','--format','fixture','--scale','2','--code-width','960','--png-root',str(p/'archive')],env=e)
