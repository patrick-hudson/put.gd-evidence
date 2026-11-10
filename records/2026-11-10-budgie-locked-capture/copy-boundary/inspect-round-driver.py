import json,sys,time,statistics
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
r='/home/patrick/work/pg-cd/work/lab-runs/bc8';out=Path(r)/'accept'
for label,package in [('before-inspect','/tmp/pg-c-three.AppImage'),('after-inspect','/tmp/pg-c-r2.AppImage')]:
 lab.cli(r,'ui.quit');time.sleep(1)
 (out/(label+'-install.json')).write_text(json.dumps(lab.install(r,appimage=package),indent=2));(out/(label+'-start.json')).write_text(json.dumps(lab.start(r),indent=2))
 (out/(label+'-version.json')).write_text(lab.guest_session(r,'putgd-cli --version-json'))
 (out/(label+'-timing.json')).write_text(lab.guest_session(r,'python3 /tmp/pg-c-timing-inspect.py',timeout=120))
 vals=[x['milliseconds'] for x in json.loads((out/(label+'-timing.json')).read_text())['rows']]
 print(label,'mean',statistics.mean(vals),'median',statistics.median(vals),'worst',max(vals),flush=True)
 (out/(label+'-load.txt')).write_text(lab.ssh(r,'cat /proc/loadavg'))
