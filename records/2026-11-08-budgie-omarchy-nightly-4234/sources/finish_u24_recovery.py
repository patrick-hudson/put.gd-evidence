import json,shlex,sys,shutil
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab,nightly_desktops as n
from tools.lab.desktop_lock import Desktop
run=Path('work/lab-runs/np1').resolve();out=Path('work/np/u24-recovery');rowout=Path('work/np/r1');row=json.loads((rowout/'result.json').read_text());session=row['session']
assert json.loads((out/'s3-independent-head.json').read_text())['verified']
for attempt in ('s3_region_upload-1','s3_region_upload-2','proton_region_upload-1','proton_region_upload-2'):
 proof=json.loads((out/(attempt+'.json')).read_text());assert proof['complete'] and proof['historyCleared'] and proof['profilesCleared'] and proof['credentialCleanup']
 root=proof['root']
 code='''import os,shutil,stat,json
from pathlib import Path
r=Path(ROOT);s=r.lstat();assert r.resolve()==r and r.parent==Path('/dev/shm') and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o700
for p in Path('/proc').glob('[0-9]*'):
 try:
  if p.stat().st_uid!=os.getuid():continue
  values=(p/'environ').read_bytes().split(b'\\0')
  assert ('XDG_RUNTIME_DIR='+str(r/'runtime')).encode() not in values,'owned root still has a live process'
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
for line in Path('/proc/self/mountinfo').read_text().splitlines():
 m=Path(line.split()[4].replace(chr(92)+'040',' '));assert m!=r and not m.is_relative_to(r)
for fx in r.glob('fx-*'):
 assert fx.is_dir() and not fx.is_symlink() and (fx/'owner').is_file() and (fx/'owner').read_text()[:8]==fx.name[3:]
shutil.rmtree(r);assert not r.exists();print(json.dumps({'privateRootRemoved':True}))
'''.replace('ROOT',repr(root))
 result=json.loads(lab.guest_session(run,'python3 - <<\'PY\'\n'+code+'\nPY\n'))
 proof.update(result);n.save(out/(attempt+'.json'),proof)
assert Desktop(Path.home()/'putgd-lab/locks','f44',resource='proton').status()['state']=='free'
slot=Path.home()/'putgd-lab/locks/tier1-guest.lock.d';assert (slot/'session').read_text().strip()==session
owner=json.loads((slot/'owner.json').read_text());assert owner['run']==str(run) and owner['session']==session
for name in ('session','owner.json','retained.json'):(slot/name).unlink()
slot.rmdir();n.save(out/'slot-release.json',dict(session=session,verifiedClean=True,run=str(run)))
profiles=Path('work/np/u24-prepare/profiles');snapshot=rowout/'profile-policy-original';shutil.copytree(profiles,snapshot)
assert all(n.digest(snapshot/name)==digest for name,digest in json.loads((rowout/'profile-sha256.json').read_text()).items())
fragment=profiles/'ubuntu-budgie-2404.d/zz-private-banners.json';fragment.parent.mkdir(parents=True,exist_ok=True);n.save(fragment,{'file_manager':{'show_banners':True}})
c=json.loads(Path('work/np/r1-config.json').read_text());c.update(output=str(Path('work/np/r1b').resolve()),flows=['history_delete','upload_clipboard','file_manager_upload','s3_region_upload','proton_region_upload']);n.save(Path('work/np/r1b-config.json'),c)
print('Retained roots, history, profiles, credentials and exact guest slot cleaned; rerun configured')
