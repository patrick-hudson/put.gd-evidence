"""Recover retained r1 publications using their exact owned receipt identities."""
import json,re,shlex,sys,os,subprocess
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab,nightly_desktops as n,proton_lab,provision_live_credentials as bridge
run=Path('work/lab-runs/np1').resolve();rowout=Path('work/np/r1').resolve();out=Path('work/np/u24-recovery').resolve();out.mkdir(mode=0o700,exist_ok=True)
session=json.loads((rowout/'result.json').read_text())['session']
assert (Path.home()/'putgd-lab/locks/tier1-guest.lock.d/session').read_text().strip()==session
lab.verify_owned_guest(run)
lab.put(run,'work/np/recover_guest_publication.py','/dev/shm/np-recover-publication.py')
for attempt in sorted(rowout.glob('*_region_upload-*')):
 if not (attempt/'receipt.json').exists():continue
 receipt=json.loads((attempt/'receipt.json').read_text());e=receipt['environment']
 if not e.get('cleanup_errors'):continue
 provider='proton' if attempt.name.startswith('proton_') else 's3'
 proof_path=out/(attempt.name+'.json')
 if proof_path.exists() and json.loads(proof_path.read_text()).get('complete'):continue
 root=e['placement_details']['session_root'];assert re.fullmatch('/dev/shm/n[0-9a-f]{8}',root)
 notes=' '.join(r.get('note','') for r in receipt['interactions'])
 ids=sorted(set(re.findall(r'historyId=([0-9a-f-]{36})',notes)));assert len(ids)==1
 code="import json,os,stat;from pathlib import Path;r=Path(ROOT);s=r.lstat();assert r.resolve()==r and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o700;v=json.loads((r/'config/putgd/config.json').read_text());assert len(v['profiles'])==1;print(json.dumps({'reference':v['profiles'][0]['credentials']['reference']}))".replace('ROOT',repr(root))
 metadata=json.loads(lab.guest_session(run,'python3 -c '+shlex.quote(code)))
 reference=metadata['reference'];bridge.validate_reference(reference,lab_only=True)
 guestproof='/dev/shm/np-proof-'+Path(root).name+'.json'
 params=dict(root=root,provider=provider,reference=reference,historyIds=ids,proof=guestproof)
 n.save(out/(attempt.name+'-params.json'),params)
 lab.put(run,out/(attempt.name+'-params.json'),'/dev/shm/np-recover-params.json')
 n.command([sys.executable,'tools/diagnostics/check_socket_paths.py','--socket',root+'/runtime/putgd/session.sock'],log=out/(attempt.name+'-sockets.json'))
 command='python3 /dev/shm/np-recover-publication.py /dev/shm/np-recover-params.json'
 if provider=='proton':
  # Re-lend through the standard baton process into the original, already-cleaned LAB reference.
  def runner(argv,env):
   original=dict(os.environ)
   try:
    os.environ.update({k:v for k,v in env.items() if k.startswith('PUTGD_LAB_')})
    text=lab.guest_session(run,command,timeout=900)
    (out/(attempt.name+'-guest-output.json')).write_text(text)
    return 0
   finally:
    for k in list(os.environ):
     if k.startswith('PUTGD_LAB_') and k not in original:os.environ.pop(k)
    os.environ.update(original)
  result=proton_lab.lend(proton_lab.Layout(),str(run),session,'np1275','recover exact retained synthetic share',['guest-recovery'],runner=runner,guest_reference=reference)
  n.save(out/(attempt.name+'-lend.json'),result)
  assert result.get('testExit')==0
 else:
  (out/(attempt.name+'-guest-output.json')).write_text(lab.guest_session(run,command,timeout=900))
 proof=json.loads(lab.ssh(run,'cat '+shlex.quote(guestproof)))
 if provider=='s3':
  guest=proton_lab.Guest(run);broker=guest.place_brokers(Path.home()/'putgd-lab/proton/guest-bridge')['qt']
  cleanup=bridge.cleanup(dict(op='cleanup',provider='s3',run=str(run),guestBroker=broker,reference=reference,receipt=str(attempt/'s3-bridge.json')))
  assert cleanup['state']=='cleanup_confirmed';guest.remove_brokers()
  proof['credentialCleanup']='cleanup_confirmed'
 else:proof['credentialCleanup']='standard Proton carry-back and guest-entry cleanup'
 proof['complete']=True;n.save(proof_path,proof)
 print(attempt.name,'remote cleanup, history, profiles and credential cleanup complete',flush=True)
