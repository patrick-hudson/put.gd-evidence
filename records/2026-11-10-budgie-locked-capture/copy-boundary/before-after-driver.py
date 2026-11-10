import json,sys,shlex,time,statistics
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
r='/home/patrick/work/pg-cd/work/lab-runs/bc8';out=Path(r)/'accept'
(out/'before-quit.json').write_text(json.dumps(lab.cli(r,'ui.quit'),indent=2));time.sleep(1)
(out/'after-install.json').write_text(json.dumps(lab.install(r,appimage='/tmp/pg-c-r2.AppImage'),indent=2));(out/'after-start.json').write_text(json.dumps(lab.start(r),indent=2))
v=json.loads(lab.guest_session(r,'putgd-cli --version-json'));expected=json.loads(Path('/tmp/pg-c-r2-build-info.json').read_text());assert v==expected
(out/'after-version.json').write_text(json.dumps(v,indent=2));(out/'after-capabilities.json').write_text(json.dumps(lab.cli(r,'capabilities'),indent=2))
(out/'after-timing.json').write_text(lab.guest_session(r,'python3 /tmp/pg-c-timing.py',timeout=120))
summary={}
for name in ('before','after'):
 rows=json.loads((out/(name+'-timing.json')).read_text())['rows'];vals=[x['milliseconds'] for x in rows]
 summary[name]={'n':len(vals),'meanMs':statistics.mean(vals),'medianMs':statistics.median(vals),'worstMs':max(vals),'bestMs':min(vals),'version':json.loads((out/(name+'-version.json')).read_text())}
summary['deltaMeanMs']=summary['after']['meanMs']-summary['before']['meanMs'];summary['deltaMedianMs']=summary['after']['medianMs']-summary['before']['medianMs']
summary['method']='Same fresh one-output1280x800,2vCPU software guest. Full production session invoke-to-terminal time, 5ms polling; 20 completed captures per version, one warm-up each excluded; includes encoding/archive/copy and is not isolated witness latency.'
(out/'timing-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)
# One actual successful image and independent console witness from this head.
op=json.loads((out/'after-timing.json').read_text())['rows'][-1]['operation'];lab.get(r,op['items'][0]['local']['path'],out/'after-capture.png');Image.open(lab.screenshot(r,'after-capture-witness')['path']).save(out/'after-capture-witness.png')
(out/'after-live-idle.txt').write_text(lab.guest_session(r,'wlopm; cat /proc/loadavg; systemctl --user is-active putgd-lab-visible.service'))
lab.guest_session(r,'busctl --user call org.buddiesofbudgie.BudgieScreenlock /org/buddiesofbudgie/Screenlock org.buddiesofbudgie.BudgieScreenlock Lock');time.sleep(1)
Image.open(lab.screenshot(r,'locked')['path']).save(out/'locked.png')
(out/'locked-state.txt').write_text(lab.guest_session(r,'wlopm; loginctl show-session 1 -p LockedHint; pgrep -x gtklock'))
before=lab.ssh(r,'find /home/lab/pg-evidence/captures -type f | sort')
for i in range(3):
 start=time.monotonic();oid=lab.cli(r,'action.invoke',{'action':'desktop'})['operationId']
 for _ in range(100):
  op=next(x for x in lab.cli(r,'operation.recent')['operations'] if x['id']==oid)
  if op['state'] in ('completed','failed','cancelled'):break
  time.sleep(.1)
 row={'milliseconds':round((time.monotonic()-start)*1000),'operation':op};(out/('locked-'+str(i)+'.json')).write_text(json.dumps(row,indent=2));assert op['state']=='failed' and op['error']['code']=='session_locked' and not op['items'];print('gtklock',i+1,row['milliseconds'],'ms',flush=True)
after=lab.ssh(r,'find /home/lab/pg-evidence/captures -type f | sort');assert before==after
(out/'locked-no-new-files.json').write_text(json.dumps({'unchanged':True,'before':before.splitlines(),'after':after.splitlines()},indent=2))
