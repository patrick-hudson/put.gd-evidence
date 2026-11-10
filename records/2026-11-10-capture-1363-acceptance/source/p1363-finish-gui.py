import sys,json
from pathlib import Path
from PIL import Image
R=sys.argv[1];E=Path.home()/'work/i1363/work/acceptance-1363'/R
read=lambda n:json.loads((E/(n+'.json')).read_text())
completed=['key-monitor-head1','monitor-exception-result','window-delay','tray-delay','rail-region-delayed','plain-shortcut-region','key-repeat']
for name in completed:assert read(name)['state']=='completed',name
assert read('key-repeat-empty')['error']['code']=='repeat_unavailable'
cancel=read('gui-click-cancel');assert cancel['state']=='cancelled' and not cancel['items'],cancel
for name in ['window-delay','tray-delay']:assert read(name+'-pill-omission')['pass'],name
bindings=read('bound-capabilities')['source']['shortcuts']['bindings'];assert all(bindings[a]['bound'] for a in ['monitor','repeat'])
for name in ['rail-region-delayed','plain-shortcut-region','key-repeat']:assert Image.open(E/(name+'.png')).size==(300,200),name
assert Image.open(E/'key-monitor-head1.png').size==(1024,768)
pixels=read('key-repeat-pixels');assert pixels['samePixels'] or pixels['knownHyprlandCornerCursorObserved']
route=read('different-default-route')['document'];assert route['actions']['monitor']['destination']=='local' and route['captureDefaults']['destination']=='upload'
assert not read('monitor-exception-result')['destination']['profileId']
diag=read('diagnostics-current');assert diag['build']['gitTree']=='1e2d35a411dc2f281b3c3414c87503a62476eba8'
report={'completed':True,'passed':True,'build':diag['build'],'qt':diag.get('qtVersion'),'cases':completed+['both bindings via Settings','empty repeat refused via real key','monitor output exception via Settings','GUI countdown click cancelled'],'knownHyprlandCornerCursorObserved':pixels.get('knownHyprlandCornerCursorObserved',False),'proofOperations':{name:read(name)['id'] for name in completed+['key-repeat-empty','gui-click-cancel']}}
(E/'gui-results.json').write_text(json.dumps(report,indent=2));(E/'gui-finished').touch();print('GUI acceptance complete',R,report['qt'])
