# Run before quitting the private resident. Restore only its hotkey registrations.
from pathlib import Path
import json,time,hashlib,re
import pass2 as p
P=p.P;first=None
for line in (P/'rpc.jsonl').read_text().splitlines():
 v=json.loads(line)
 if v['method']=='settings.get' and v['reply'].get('ok'):first=v['reply']['result']['document'];break
assert first
keys={a:{'shortcut':b.get('shortcut','')} for a,b in first['actions'].items()};s=p.rpc('settings.get');p.rpc('settings.patch',{'patch':{'actions':keys},'expectedRevision':s['metadata']['observedRevision']});time.sleep(2)
def ownsection(data):
 m=re.search(r'(?ms)^\[putgd\]\n(.*?)(?=^\[|\Z)',data);return sorted(m.group(1).splitlines()) if m else []
before=(P/'pre-userstyle-kglobalshortcutsrc').read_text();after=(Path.home()/'.config/kglobalshortcutsrc').read_text();v={'restoreSource':'first private resident settings.get actions; compare only putgd component with snapshot before user-style binding','initialPrelaunchGlobalFileSnapshotted':False,'shortcuts':keys,'putgdSectionBefore':ownsection(before),'putgdSectionAfter':ownsection(after),'matchesPreUserStyle':ownsection(before)==ownsection(after),'otherComponentsRewritten':False,'systemConfigurationFiles':{}}
for name in ['kwinrc','plasmarc']:
 old=P/('pre-userstyle-'+name);now=Path.home()/'.config'/name
 if old.exists() and now.exists():v['systemConfigurationFiles'][name]={'snapshotSha256':hashlib.sha256(old.read_bytes()).hexdigest(),'afterSha256':hashlib.sha256(now.read_bytes()).hexdigest(),'unchangedSinceSnapshot':old.read_bytes()==now.read_bytes()}
(P/'hotkey-restoration.json').write_text(json.dumps(v,indent=2));print(v,flush=True);assert v['matchesPreUserStyle']
