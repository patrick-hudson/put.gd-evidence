import os,sys,pathlib,json,subprocess
roots=json.loads(sys.argv[1]);receipt=[]
for value in roots:
 p=pathlib.Path(value)
 if not p.exists():continue
 assert p.is_dir() and not p.is_symlink() and p.resolve()==p and p.stat().st_uid==os.getuid(),value
 assert str(p) in ('/home/patrick/repo1428','/home/patrick/work/r1428') or (str(p.parent)=='/tmp' and p.name.startswith('r1428-'))
 assert not list(p.rglob('disk.qcow2')),'Overlay must already be retired'
 files=subprocess.check_output(['find',str(p),'!','-type','d','-print0'])
 names=[os.fsdecode(x) for x in files.split(b'\0') if x]
 print(json.dumps({'root':str(p),'exactFiles':names}),flush=True)
 if names:subprocess.run(['xargs','-0','rm','-f','--'],input=files,check=True)
 dirs=subprocess.check_output(['find',str(p),'-depth','-type','d','-print0'])
 for d in dirs.split(b'\0'):
  if d:os.rmdir(d)
 receipt.append({'root':str(p),'filesRemoved':len(names),'absentAfter':not p.exists()})
print(json.dumps({'cleanup':receipt,'ok':True}),flush=True)
