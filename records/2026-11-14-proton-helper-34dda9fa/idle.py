import os,json,time,hashlib,socket,struct,sys
from pathlib import Path
# The driver already waits 35 seconds after the UI exits. The native matrix
# specifies 180 seconds of idle before evaluating its budget.
time.sleep(145)
work=Path(sys.argv[1]);endpoint=str(work/'profile/runtime/putgd/session.sock');assert len(endpoint.encode())<=107
s=socket.socket(socket.AF_UNIX);s.connect(endpoint);pid,uid,gid=struct.unpack('3i',s.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));s.close();assert uid==os.getuid()
stat=lambda p:(Path(f'/proc/{p}/stat').read_text().split(') ',1)[1].split())
ticks=stat(pid)[19];identities={}
for name in ['putgd','putgd-cli','putgd-ui']:
 import subprocess
 path=Path('/usr/bin')/name
 x=json.loads(subprocess.check_output([path,'--version-json']));assert x['gitCommit']=='ff636bba2bee89caccf9dddeb1a4992d0a411acd' and not x['dirty']
 identities[name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'build':x}
libs=sorted({Path(line.split()[-1]).name for line in Path(f'/proc/{pid}/maps').read_text().splitlines() if '.so' in line})
report={'settlingSecondsAfterUiExit':180,'libraries':libs,'pid':pid,'startTicks':ticks,'binaries':identities,'windows':[],'passed':False}
accepted=0
for n in range(1,5):
 quiet_deadline=time.monotonic()+180
 while os.getloadavg()[0]>1:
  if time.monotonic()>quiet_deadline:
   report['blocked']='host load stayed above 1 before the observation';(work/'new-idle.json').write_text(json.dumps(report,indent=2));raise SystemExit(2)
  time.sleep(2)
 import subprocess
 import desktop_lock
 locks=desktop_lock.Desktop(Path.home()/'putgd-lab/locks',os.environ['W7_HOST']).status()
 assert locks.get('lock',{}).get('session')==os.environ['W7_SESSION']
 q=subprocess.run(['pgrep','-c','qemu-system'],capture_output=True,text=True)
 build=[line.split()[-1] for line in subprocess.run(['ps','-eo','stat=,comm='],capture_output=True,text=True).stdout.splitlines() if line.split() and not line.split()[0].startswith('Z')]
 builders=[p.strip() for p in build if p.strip() in ('ninja','cc1plus','clang','clang++','cmake','ctest','rustc')]
 preflight={'qemuCount':int(q.stdout.strip() or '0'),'builders':builders,'uptime':subprocess.check_output(['uptime'],text=True).strip(),'lockSession':locks['lock']['session'],'lockPurpose':locks['lock']['purpose']}
 (work/f'quiet-preflight-{n}.json').write_text(json.dumps(preflight,indent=2))
 assert preflight['qemuCount']==0 and not builders,'host is not quiet: VM or builder present'
 start=time.monotonic();rows=[]
 while time.monotonic()-start<301:
  assert stat(pid)[19]==ticks
  family=[];busy=[]
  for p in Path('/proc').iterdir():
   if not p.name.isdigit():continue
   try:
    comm=(p/'comm').read_text().strip()
    if (comm.startswith('qemu-system') or comm in ('ninja','cc1plus','clang','clang++','cmake','ctest','rustc')) and stat(p.name)[0]!='Z':busy.append(comm)
    if p.stat().st_uid!=os.getuid():continue
   except FileNotFoundError:continue
   if not comm.startswith('putgd'):continue
   try:
    a=stat(p.name);m={}
    for line in (p/'smaps_rollup').read_text().splitlines():
     k,_,v=line.partition(':')
     if k in ('Rss','Pss','Private_Clean','Private_Dirty','Swap'):m[k]=int(v.split()[0])*1024
    family.append(dict(pid=int(p.name),startTicks=a[19],cpuTicks=int(a[11])+int(a[12]),exe=os.readlink(p/'exe'),memory=m))
   except FileNotFoundError:continue
  rows.append(dict(at=time.monotonic(),load=os.getloadavg(),busy=busy,processes=family));time.sleep(.2)
 (work/f'new-idle-{n}-samples.json').write_text(json.dumps(rows))
 elapsed=rows[-1]['at']-rows[0]['at']; assert elapsed>=300
 assert all(len(r['processes'])==1 and r['processes'][0]['pid']==pid for r in rows)
 cpu=(rows[-1]['processes'][0]['cpuTicks']-rows[0]['processes'][0]['cpuTicks'])/os.sysconf('SC_CLK_TCK')/elapsed*100
 peak=lambda k:max(r['processes'][0]['memory'][k] for r in rows)
 gates=dict(rss=peak('Rss')<=40*1048576,pss=peak('Pss')<=40*1048576,cpu=cpu<.5,swap=peak('Swap')==0,quiet=all(r['load'][0]<1 and not r['busy'] for r in rows),noHelpers=True)
 (work/f'new-idle-{n}-samples.json').write_text(json.dumps(rows))
 report['windows'].append(dict(index=n,elapsed=elapsed,cpuPercent=cpu,rssPeak=peak('Rss'),pssPeak=peak('Pss'),gates=gates))
 if gates['quiet']:
  if not all(gates.values()):break
  accepted+=1
 (work/'new-idle.json').write_text(json.dumps(report,indent=2));print('window',n,gates,flush=True)
 if accepted==2:break
report['passed']=accepted==2 and all(all(w['gates'].values()) for w in report['windows'] if w['gates']['quiet']);(work/'new-idle.json').write_text(json.dumps(report,indent=2))
