from pathlib import Path
import json,hashlib,shutil
ns={};exec(Path('/home/patrick/work/svm1398/v2analyze.py').read_text().split('out=json.loads')[0],ns)
base=Path('/home/patrick/work/svm1398/v2evidence');out={}
for k in 'obnk':
 p=base/k;entry={}
 if (p/'native/cases').exists():
  entry['native']={}
  for d in (p/'native/cases').iterdir():
   r=json.loads((d/'result.json').read_text());v=ns['ruler'](d/'capture.png',2400,codewidth=960) if (d/'capture.png').exists() else None;entry['native'][d.name]={'capture':r.get('capture'),'error':r.get('error'),'verification':v}
 if (p/'user-final-history.json').exists():
  r=json.loads((p/'user-final-history.json').read_text())['records'][0];f=p/'final'/r['local']['path'].removeprefix('/tmp/v2/')
  assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'];shutil.copyfile(f,p/'user-capture.png');entry['user']={'historyId':r['id'],'operationId':r['operationId'],'sha256':r['sha256'],'uploadStatus':r['uploadStatus'],'verification':ns['ruler'](f,None,codewidth=960)};(p/'user-raster-verification.json').write_text(json.dumps(entry['user'],indent=2))
 out[k]=entry
 print(k,{n:({q:v['verification'] for q,v in val.items()} if n=='native' else val) for n,val in entry.items()},flush=True)
(base/'extras-analysis.json').write_text(json.dumps(out,indent=2))
