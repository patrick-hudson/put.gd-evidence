from pathlib import Path
import sys,shlex,json,base64,concurrent.futures,subprocess
B=Path(__file__).parent;G=B/'2026-11-12-scroll-accept2-1398';sys.path.insert(0,str(B.parent/'review'));import control
common=['export-scroll-accept2.py','delete-scroll-accept2.py','scroll-accept2-export.log','scroll-accept2-delete.log'];extra={'d69':['archive-guest-host-accept2.py','delete-guest-host-accept2.py','guest-host-archive.log','guest-host-delete.log','archive-cap-host.py','delete-cap-owned.py','cap-host-archive.log'],'m74':['export-mint-sm2.py','delete-sm2-owned.py','sm2-export.log'],'f44':[]}
def run(h):
 code="""from pathlib import Path
import json,os,stat,hashlib,shutil,time
r=Path('/home/patrick/work');a=r/'scroll-accept2-archive/cleanup-tools';a.mkdir(exist_ok=True);entries=[]
for n in NAMES:
 p=r/n
 if not p.exists():continue
 s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid(),str(p);data=p.read_bytes();q=a/n
 if q.exists():assert q.read_bytes()==data
 else:q.write_bytes(data)
 v={'path':str(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'inode':s.st_ino};assert p.lstat().st_ino==s.st_ino;p.unlink();v['absent']=not p.exists();entries.append(v)
own=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  args=(p/'cmdline').read_bytes().split(bytes([0]))
  if any(x.startswith(b'/home/patrick/work/'+s) for x in args for s in [b'sa2/',b'sl25/',b'sf2/',b'sd2/',b'sq3/',b'sq4/',b'sm2/',b'sa2lab/',b'sa2vm/',b'sc2/']):own.append(int(p.name))
 except OSError:pass
v={'removedOwnedFiles':entries,'ownedScratchProcesses':own,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};(r/'scroll-accept2-archive/final-helper-cleanup.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
""".replace('NAMES',repr(common+extra[h]));r=control.ssh(h,'python3 -c '+shlex.quote(code),capture_output=True,text=True,check=True);v=json.loads(r.stdout);(G/'cleanup'/h/'final-helper-cleanup.json').write_text(json.dumps(v,indent=2));return h,len(v['removedOwnedFiles']),v['ownedScratchProcesses']
with concurrent.futures.ThreadPoolExecutor() as pool:
 for r in pool.map(run,['m74','f44','d69']):print(r)
p=subprocess.run(['python3','tools/lab/desktop_lock.py','status','m74','f44','d69','--json'],capture_output=True,text=True,check=True);(G/'cleanup/final-lock-status.json').write_text(p.stdout)
