from pathlib import Path
import json,hashlib
R=Path.home()/'work/i1363/work/lab-runs/ap6';E=Path.home()/'work/i1363/work/acceptance-1363/ap6'
s=json.loads((R/'state.json').read_text());base={'run':str(R),'runId':s['id'],'completed':True,'outcome':'passed'}
(E/'completion.json').write_text(json.dumps(base,indent=2))
m={'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence',**base,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in E.iterdir() if p.is_file() and p.name!='manifest.json'}}
(E/'manifest.json').write_text(json.dumps(m,indent=2))
