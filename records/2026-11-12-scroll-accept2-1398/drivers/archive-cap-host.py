from pathlib import Path
import os,json,hashlib,tarfile,time,stat
A=Path('/home/patrick/work/scroll-accept2-archive');roots=[Path('/home/patrick/work/sc2')];runs=roots[0]/'work/lab-runs';expected={'co','cb','cn','ck'};assert {d.name for d in runs.iterdir() if d.is_dir()}==expected;assert not list(roots[0].rglob('*.qcow2'))
for d in runs.iterdir():
 s=json.loads((d/'state.json').read_text());assert not (Path('/proc')/str(s['pid'])).exists(),s['pid'];assert (roots[0]/'evidence'/d.name[1:]/'workstation-verified.json').exists();assert '"status": "completed"' in (roots[0]/'evidence'/d.name[1:]/'cleanup-result.json').read_text()
files=[];manifest={};excluded=[]
for root in roots:
 for f in root.rglob('*'):
  if f.is_symlink() or not f.is_file():continue
  assert f.stat().st_uid==os.getuid(),str(f)
  if f.name in ['identity','credentials.txt']:
   excluded.append({'path':str(f),'reason':'temporary authentication input; excluded from evidence'});continue
  rel=root.name+'/'+str(f.relative_to(root));files.append((f,rel));manifest[rel]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
M=A/'cap-proof-host-cold-manifest.json';M.write_text(json.dumps({'files':manifest,'excludedAuthenticationInputs':excluded},indent=2));arc=A/'cap-proof-host-cold.tgz'
with tarfile.open(arc,'w:gz',compresslevel=1) as t:
 t.add(M,arcname='manifest.json')
 for f,rel in files:t.add(f,arcname=rel,recursive=False)
with tarfile.open(arc) as t:
 for m in t:
  if m.name=='manifest.json':continue
  assert hashlib.sha256(t.extractfile(m).read()).hexdigest()==manifest[m.name]['sha256'],m.name
v={'roots':[str(r) for r in roots],'filesVerified':len(files),'archiveSha256':hashlib.sha256(arc.read_bytes()).hexdigest(),'verified':True,'authenticationFilesExcluded':len(excluded),'allOverlaysRetired':True,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};(A/'cap-proof-host-cold-verified.json').write_text(json.dumps(v,indent=2));print(json.dumps(v),flush=True)
