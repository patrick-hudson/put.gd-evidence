"""Private row runner: same FLOWS/recipes/verdicts, with no publisher or controller call."""
import argparse,json,os,subprocess,sys,uuid,time,datetime,shutil
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab,nightly_desktops as n
p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);a=p.parse_args()
c=json.loads(n.private_file(a.config).read_text());row=c['row'];run=Path(c['run']);out=Path(c['output']);out.mkdir(mode=0o700,parents=True,exist_ok=False)
identity=json.loads(Path(c['identity']).read_text());session='np1275-'+uuid.uuid4().hex[:12]
assert subprocess.check_output(['git','merge-base','--is-ancestor','2b5e1b2d3',identity['gitCommit']]).decode()==''
assert c['tag']!='v26.1108.4139-nightly'
lab.verify_owned_guest(run)
slot=Path.home()/'putgd-lab/locks/tier1-guest.lock.d';slot.mkdir(mode=0o700)
n.save(slot/'owner.json',dict(run=str(run),session=session,worker=n.worker_identity(),evidence=str(out)))
(slot/'session').write_text(session+'\n');(slot/'session').chmod(0o600)
assert c.get('attempts',2) in (1,2)
selected=c.get('flows',list(n.FLOWS));assert selected and all(flow in n.FLOWS for flow in selected)
cells={flow:n.cell(assertion='not started') for flow in selected}
record=dict(desktop=row['desktop'],package=row['package'],host=c['host'],release=c['tag'],build=identity['gitCommit'],driver=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),session=session,run=str(run),cells=cells)
def save():n.save(out/'result.json',record)
n.save(out/'run-config.json',c)
n.save(out/'profile-sha256.json',{str(p.relative_to(Path(c['profiles']))):n.digest(p) for p in sorted(Path(c['profiles']).rglob('*.json'))})
info=lab.state(run);package=json.loads((run/'package.json').read_text())
record.update(goldenSha256=info['golden_sha256'],packageSha256=package['sha256'],driverScriptSha256=n.digest(Path(__file__)))
shutil.copy2(Path(__file__),out/'driver.py')
assert n.digest(out/'driver.py')==record['driverScriptSha256']
save()
now=datetime.datetime.now(datetime.timezone.utc)
cutoff=datetime.datetime.fromisoformat(c['campaignCutoffUtc'])
assert cutoff.tzinfo is not None
deadline=time.monotonic()+min(4*3600,(cutoff-now).total_seconds())
try:
 for flow in cells:
  if time.monotonic()>=deadline:
   cells[flow].update(assertion='private campaign deadline reached; release guest slots before 07:15 UTC');save();continue
  dest='s3' if flow.startswith('s3_') else 'proton' if flow.startswith('proton_') else 'local'
  recipe=('outcomes.' if dest=='local' else 'outcomes_live.')+flow
  for attempt in range(1,c.get('attempts',2)+1):
   name=flow+'-'+str(attempt);target=out/name;runtime='/dev/shm/n'+uuid.uuid4().hex[:8]
   n.command([sys.executable,'tools/diagnostics/check_socket_paths.py','--socket',target/'runtime/putgd/session.sock',runtime+'/runtime/putgd/session.sock'],log=out/(name+'-sockets.json'))
   args=[sys.executable,'-m','tools.lab.surface_driver.run','--desktop',row['desktop'],'--host',c['host'],'--placement','guest','--guest',row['profile'],'--run',str(run),'--package',row['package'],'--destination',dest,'--recipes',recipe,'--catalog',c['catalog'],'--build',identity['gitCommit'],'--profiles',c['profiles'],'--session-root',runtime,'--out',str(target),'--campaign','private-budgie-omarchy','--coverage',str(out/(name+'-coverage.json'))]
   if dest=='proton':args=[sys.executable,'tools/lab/proton_lab.py','lend',str(run),'--session',session,'--owner','np1275','--purpose','private nightly VM outcome','--']+args
   env=dict(os.environ,PUTGD_TIER1_SESSION=session,HOME=str(Path.home().resolve()))
   try:n.command(['nice','-n','10',*args],log=out/(name+'.log'),env=env,timeout=max(1,min(1800,deadline-time.monotonic())))
   except (RuntimeError,subprocess.TimeoutExpired):pass
   observed=n.verdict(target,recipe);observed['attempt']=attempt;cells[flow].setdefault('attempts',[]).append(observed);cells[flow].update(observed);save();print(flow,observed['status'],observed.get('assertion'),flush=True)
   if observed['status']=='green':break
finally:
 record['finishedAt']=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat();save()
 # Keep the durable slot on any explicit retained cleanup, otherwise free only our own.
 retained=False
 for receipt in out.glob('*/receipt.json'):
  e=json.loads(receipt.read_text()).get('environment',{})
  retained |= bool(e.get('cleanup_errors')) or 'retained' in str(e.get('private_cleanup',''))
 proton=Path.home()/'putgd-lab/locks/proton.lock'
 retained |= proton.exists() and 'lent copy outstanding' in proton.read_text()
 if not retained:
  assert (slot/'session').read_text().strip()==session
  (slot/'session').unlink();(slot/'owner.json').unlink();slot.rmdir()
 else:n.save(slot/'retained.json',dict(run=str(run),session=session,evidence=str(out)))
