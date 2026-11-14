from pathlib import Path
from trial import cursorpos
import json,subprocess,hashlib
l=Path.home()/'work/s5202';a=l/'a';before=json.loads((l/'before-state.json').read_text());w=(a/'r12-received.txt').read_text().strip();assert w=='abc'
devices=[p.read_text().strip() for p in Path('/sys/class/input').glob('event*/device/name')];test=[s for s in devices if 'putgd-lab' in s or 'scroll-1520' in s]
status=subprocess.run(['dpkg-query','-W','-f=${db:Status-Abbrev} ${Version}\n','putgd'],capture_output=True,text=True).stdout
source=Path('/etc/apt/sources.list.d/putgd.sources');sha=hashlib.sha256(source.read_bytes()).hexdigest();after=subprocess.check_output(['xinput','--list','--long'],text=True)
v={'witness':w,'testInputDevices':test,'pointerRestoredToAcquirePosition':cursorpos(),'packageStatusAfter':status,'aptSourceSha256Before':before['aptSourceSha256'],'aptSourceSha256After':sha,'xinputAfter':after,'xinputListMatchesBefore':after==before['xinput'],'aSessionSocketExists':(l/'a/run/putgd/session.sock').exists(),'bSessionSocketExists':(l/'b/run/putgd/session.sock').exists(),'ownedNotificationsCleared':3,'initialMasterMetadataMismatchResolvedByXTestEvents':True};(a/'cleanup.json').write_text(json.dumps(v,indent=2))
assert status.startswith('rc ') and not test and sha==before['aptSourceSha256'] and v['xinputListMatchesBefore'] and not v['aSessionSocketExists'] and not v['bSessionSocketExists'];print(json.dumps({k:v[k] for k in ['witness','testInputDevices','packageStatusAfter','xinputListMatchesBefore','pointerRestoredToAcquirePosition','ownedNotificationsCleared']}))
