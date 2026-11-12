from pathlib import Path
import os,stat,json,hashlib,sys,time
root=Path(sys.argv[1]);out=Path(sys.argv[2]);assert str(root) in ['/home/patrick/work/sc2'];assert root.resolve()==root and root.is_dir() and root.stat().st_uid==os.getuid()
assert json.loads((out.parent/'cap-proof-host-cold-verified.json').read_text())['verified']
entries=[];dirs=[]
for base,ds,fs in os.walk(root,followlinks=False):
 b=Path(base);dirs.append(b)
 for name in list(ds):
  f=b/name
  if f.is_symlink():fs.append(name);ds.remove(name)
 for name in fs:
  f=b/name;s=f.lstat();assert s.st_uid==os.getuid(),str(f);v={'path':str(f),'device':s.st_dev,'inode':s.st_ino,'mode':s.st_mode,'size':s.st_size}
  if stat.S_ISREG(s.st_mode):v['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
  entries.append(v)
out.write_text(json.dumps({'root':str(root),'files':entries,'directories':[str(d) for d in dirs]},indent=2))
for v in entries:
 f=Path(v['path']);s=f.lstat();assert (s.st_dev,s.st_ino,s.st_mode,s.st_size)==(v['device'],v['inode'],v['mode'],v['size']),str(f)
 if 'sha256' in v:assert hashlib.sha256(f.read_bytes()).hexdigest()==v['sha256'],str(f)
 f.unlink()
for d in sorted(dirs,key=lambda d:len(d.parts),reverse=True):d.rmdir()
receipt={'root':str(root),'filesDeleted':len(entries),'directoriesRemoved':len(dirs),'rootAbsent':not root.exists(),'manifestSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};out.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
