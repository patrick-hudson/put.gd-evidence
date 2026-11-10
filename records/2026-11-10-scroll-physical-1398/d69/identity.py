from pathlib import Path
import json,subprocess,os,time
p=Path('/tmp/sp1398');e=json.loads((p/'env.json').read_text());out={}
for command in [['uname','-a'],['loginctl','list-sessions'],['putgd-cli','--version-json'],['dpkg-query','-W','cinnamon','muffin','kwin-wayland','plasma-workspace','firefox','putgd'],['rpm','-q','gnome-shell','mutter','firefox','putgd']]:
 try:r=subprocess.run(command,env=e,text=True,capture_output=True);out[' '.join(command)]={'stdout':r.stdout,'stderr':r.stderr,'exit':r.returncode}
 except FileNotFoundError:pass
(p/'identities.json').write_text(json.dumps(out,indent=2))
pid=int((p/'resident.pid').read_text());samples=[]
for _ in range(30):
 ps=[]
 for d in Path('/proc').iterdir():
  if not d.name.isdigit():continue
  try:
   env=(d/'environ').read_bytes().split(b'\0')
   if b'XDG_CONFIG_HOME=/tmp/sp1398/config' not in env:continue
   cmd=(d/'comm').read_text().strip()
   if not cmd.startswith('putgd'):continue
   status=(d/'status').read_text();rss=int(next(x.split()[1] for x in status.splitlines() if x.startswith('VmRSS:')));ps.append({'pid':int(d.name),'comm':cmd,'rssKiB':rss})
  except (FileNotFoundError,PermissionError,StopIteration,ProcessLookupError):pass
 samples.append({'time':time.time(),'processes':ps,'rssMiB':sum(x['rssKiB'] for x in ps)/1024});time.sleep(1)
(p/'memory.json').write_text(json.dumps({'targetMiB':40,'windowSeconds':30,'samples':samples,'pass':all(s['rssMiB']<40 for s in samples)},indent=2))
