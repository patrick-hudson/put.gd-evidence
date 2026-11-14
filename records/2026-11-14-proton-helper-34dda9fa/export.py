from pathlib import Path
import os,json,hashlib,tarfile,time,sys
host=sys.argv[1];prefix={'m74':'w34m','f44':'w34f','k72':'w34k'}[host];base=Path.home()/'archives/proton-p6-34dda9fa';base.mkdir(mode=0o700,parents=True,exist_ok=True);out=base/'numeric';out.mkdir(mode=0o700)
for run in sorted(Path('/tmp').glob(prefix+'[0-9]*')):
 if not run.is_dir():continue
 dest=out/run.name;dest.mkdir()
 for p in run.iterdir():
  if not p.is_file() or not (p.name in ('results.json','summary.txt','family.json','new-idle.json','history.png','unknown-findings.json') or p.name.startswith(('new-idle-','quiet-preflight-'))):continue
  raw=p.read_bytes()
  if p.name=='results.json':
   x=json.loads(raw);x.pop('providerDiagnostics',None);raw=(json.dumps(x,indent=2)+'\n').encode()
  (dest/p.name).write_bytes(raw)
 events=[]
 for log in (run/'profile/state/putgd/logs').glob('*.jsonl'):
  for line in log.read_text().splitlines():
   try:r=json.loads(line)
   except ValueError:continue
   if r.get('message') not in ('Operation accepted','Operation finished','Upload finished','Sharing finished'):continue
   f=r.get('fields',{});op=r.get('operationId') or f.get('operationId')
   if op:events.append({'time':r.get('time'),'operationId':op,'event':r['message'],**{k:f[k] for k in ('action','state','status') if k in f},'errorCode':(f.get('error') or {}).get('code')})
 (dest/'events.json').write_text(json.dumps({'events':events,'clockCorrelationSnapshot':{'utc':time.time(),'monotonic':time.monotonic()}},indent=2)+'\n')
work=Path.home()/'work/w7-34';drivers=out/'drivers';drivers.mkdir()
for p in list(work.glob('*.py'))+list(work.glob('*.log'))+list(work.glob('*before*'))+list(work.glob('*after*'))+list(work.glob('package-check.json'))+list(work.glob('environment.json'))+list((work/'drivers').glob('*')):
 if p.is_file():(drivers/p.name).write_bytes(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files={str(p.relative_to(out)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in out.rglob('*') if p.is_file()};(out/'index.json').write_text(json.dumps(files,indent=2)+'\n');archive=base/(host+'-numeric.tar.gz')
with tarfile.open(archive,'x:gz',compresslevel=3) as t:t.add(out,arcname=host)
with tarfile.open(archive) as t:
 for name,x in files.items():assert hashlib.file_digest(t.extractfile(host+'/'+name),'sha256').hexdigest()==x['sha256']
r={'host':host,'archive':str(archive),'sha256':sha(archive),'bytes':archive.stat().st_size,'memberFileCount':len(files)+1,'verifiedReadback':True,'excluded':'Private profiles, credentials, login, capability URLs, payloads and raw captures.'};(base/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
