from pathlib import Path
import json,os,datetime,subprocess,hashlib
B=Path('/home/patrick/work/svm1398');out={'host':'d69 192.168.68.69','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runs':{},'load':os.getloadavg()}
for k in 'obnk':
 r=B/'repo/work/lab-runs'/(k+'3');s=json.loads((r/'state.json').read_text());out['runs'][k]={'id':s['id'],'pid':s['pid'],'pidExists':Path('/proc',str(s['pid'])).exists(),'overlayExists':(r/'disk.qcow2').exists(),'goldenExists':Path(s['golden']).is_file(),'receiptSha256':hashlib.sha256((r/'overlay-cleanup.json').read_bytes()).hexdigest()}
assert all(not x['pidExists'] and not x['overlayExists'] and x['goldenExists'] for x in out['runs'].values())
p=subprocess.run(['sudo','-n','journalctl','-k','--since','2026-11-11 01:35:00','-q','--no-pager'],capture_output=True,text=True);out['newGpuErrorLines']=[v for v in p.stdout.splitlines() if any(t in v for t in ['GPU HANG','GL_CONTEXT_LOST'])];out['kernelJournalExit']=p.returncode
(B/'v3-host-cleanup.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
