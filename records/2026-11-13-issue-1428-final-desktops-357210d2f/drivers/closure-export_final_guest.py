from pathlib import Path
import sys,subprocess,json,hashlib,tarfile,shutil,datetime
r=Path.home()/'work/b1428';name=sys.argv[1];assert name.startswith('f') and name.isalnum();e=r/('export-'+name);e.mkdir(mode=0o700);run=r/'r/work/lab-runs'/name;g=r/'guest.py'
v=subprocess.check_output(['python3',str(g),name,'python3 /home/lab/b1428/collect_guest.py receipts.tar'],text=True);d=json.loads(v);subprocess.run(['python3',str(g),name,'--get',d['file'],str(e/'receipts.tar')],check=True);actual=hashlib.sha256((e/'receipts.tar').read_bytes()).hexdigest();assert actual==d['sha256']
for f in ['state.json','manual-launch-config.json']:
 if (run/f).exists():shutil.copy2(run/f,e/f)
for failed in r.glob(name+'-failed-attempt.tar'):shutil.copy2(failed,e/failed.name)
state=json.loads((run/'state.json').read_text());old={'fkx':'kx','fgx':'gx','fgw':'gw','fbk':'bk','fhk':'hk'}[name];previous=json.loads((r/'r/work/lab-runs'/old/'state.json').read_text());assert state['golden']==previous['golden'] and state['golden_sha256']==previous['golden_sha256']
(e/'guest-export.json').write_text(json.dumps({'name':name,'guestTarSha256':actual,'verifiedAgainstGuest':True,'goldenSha256MatchesPriorVerifiedImmutableSource':True,'exportedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2));bundle=r/('export-'+name+'.tar');assert not bundle.exists()
with tarfile.open(bundle,'w') as t:
 for f in e.iterdir():t.add(f,arcname=f.name,recursive=False)
print(json.dumps({'bundle':str(bundle),'sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'guestTarSha256':actual}))
