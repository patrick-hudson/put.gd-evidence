import sys,pathlib,json,hashlib,shutil,subprocess,shlex,fcntl,os
sys.path.insert(0,'/tmp/b1364');from control import H
E=pathlib.Path('/home/patrick/work/putgd-evidence/2026-11-10-recording-1364-budgie-final-visible');D=pathlib.Path('/tmp/b1364-visible');R=E/'retirement';R.mkdir(exist_ok=True)
s=json.loads((D/'state.json').read_text());v=json.loads((E/'identity/export-verification.json').read_text());assert not v['mismatches']
base={'run':'/home/patrick/work/put.gd/work/lab-runs/b1364v','runId':s['id'],'completed':True,'outcome':'passed'}
(R/'completion.json').write_text(json.dumps(base,indent=2)+'\n')
for src,dst in [(D/'state.json',R/'state.json'),(E/'summary.json',R/'summary.json'),(E/'identity/export-verification.json',R/'export-verification.json')]:shutil.copy2(src,dst)
m={'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence',**base,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in R.iterdir() if p.is_file()and p.name!='manifest.json'}}
(R/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
remote='/home/patrick/work/b1364/visible-retirement'
subprocess.run(H+['mkdir -p '+remote],check=True)
subprocess.run(['rsync','-a','-e',shlex.join(H[:-1]),str(R)+'/',H[-1]+':'+remote+'/'],check=True)
def host(cmd,log):
 p=subprocess.run(H+[cmd],capture_output=True,text=True);(D/log).write_text(p.stdout+p.stderr);print(p.stdout);p.check_returncode();return p.stdout
host('python3 /home/patrick/work/b1364/host_lab.py reset --run '+base['run'],'stop.log')
cmd='python3 /home/patrick/work/b1364/host_lab.py cleanup --run '+base['run']+' --evidence-manifest '+remote+'/manifest.json'
host(cmd+' --dry-run','cleanup-dry.log')
x=host(cmd,'cleanup-apply.log');assert 'completed' in x
subprocess.run(['systemctl','--user','stop','putgd-vm-1364-b1364v.service'],check=True)
p=pathlib.Path('/home/patrick/work/put.gd/tools/qemu-grid/remote-displays.json')
with open('/tmp/putgd-wall-config.lock','w')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);data=json.loads(p.read_text())
 # Preserve all unrelated entries and the surrounding schema.
 if isinstance(data,list):
  old=data;new=[x for x in old if not(x.get('name')=='Budgie recording1364 b1364v' and x.get('port')==5996)];assert len(old)-len(new)==1;data=new
 else:
  key=next(k for k,v in data.items()if isinstance(v,list)and any(isinstance(x,dict)and x.get('name')=='Budgie recording1364 b1364v' for x in v))
  old=data[key];data[key]=[x for x in old if not(x.get('name')=='Budgie recording1364 b1364v' and x.get('port')==5996)];assert len(old)-len(data[key])==1
 tmp=p.with_name(p.name+'.b1364v-tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');os.replace(tmp,p)
host('cat '+base['run']+'/overlay-cleanup.json; ps -p '+str(s['pid'])+' -o pid,args; pgrep -a qemu-system || true; test ! -e '+base['run']+'/disk.qcow2','cleanup-confirm.log')
(D/'identity').unlink() if (D/'identity').exists() else None
pathlib.Path('/tmp/b1364/identity').unlink()
for name in ('stop.log','cleanup-dry.log','cleanup-apply.log','cleanup-confirm.log'):shutil.copy2(D/name,E/'identity'/name)
subprocess.run(['rsync','-a','-e',shlex.join(H[:-1]),H[-1]+':'+base['run']+'/overlay-cleanup.json',str(R/'overlay-cleanup.json')],check=True)
