import os,json,time,hashlib,socket,struct,sys
from pathlib import Path
work=Path(sys.argv[1]);endpoint=str(work/'profile/runtime/putgd/session.sock');assert len(endpoint.encode())<=107
s=socket.socket(socket.AF_UNIX);s.connect(endpoint);pid,uid,gid=struct.unpack('3i',s.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));s.close();assert uid==os.getuid()
stat=lambda p:(Path(f'/proc/{p}/stat').read_text().split(') ',1)[1].split())
ticks=stat(pid)[19];identities={}
for name in ['putgd','putgd-cli','putgd-ui']:
 import subprocess
 path=Path('/usr/bin')/name
 x=json.loads(subprocess.check_output([path,'--version-json']));assert x['gitCommit']=='466449a4c69a07a1997668d1b70d637abac76a16' and not x['dirty']
 identities[name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'build':x}
libs=sorted({Path(line.split()[-1]).name for line in Path(f'/proc/{pid}/maps').read_text().splitlines() if '.so' in line})
report={'libraries':libs,'pid':pid,'startTicks':ticks,'binaries':identities,'windows':[],'passed':False}
accepted=0
for n in range(1,5):
 quiet_deadline=time.monotonic()+180
 while os.getloadavg()[0]>1:
  if time.monotonic()>quiet_deadline:
   report['blocked']='host load stayed above 1 before the observation';(work/'new-idle.json').write_text(json.dumps(report,indent=2));raise SystemExit(2)
  time.sleep(2)
 start=time.monotonic();rows=[]
 while time.monotonic()-start<301:
  assert stat(pid)[19]==ticks
  family=[]
  for p in Path('/proc').iterdir():
   if not p.name.isdigit():continue
   try:
    if p.stat().st_uid!=os.getuid():continue
    comm=(p/'comm').read_text().strip()
   except FileNotFoundError:continue
   if not comm.startswith('putgd'):continue
   try:
    a=stat(p.name);m={}
    for line in (p/'smaps_rollup').read_text().splitlines():
     k,_,v=line.partition(':')
     if k in ('Rss','Pss','Private_Clean','Private_Dirty','Swap'):m[k]=int(v.split()[0])*1024
    family.append(dict(pid=int(p.name),startTicks=a[19],cpuTicks=int(a[11])+int(a[12]),exe=os.readlink(p/'exe'),memory=m))
   except FileNotFoundError:continue
  rows.append(dict(at=time.monotonic(),load=os.getloadavg(),processes=family));time.sleep(.2)
 (work/f'new-idle-{n}-samples.json').write_text(json.dumps(rows))
 elapsed=rows[-1]['at']-rows[0]['at']; assert elapsed>=300
 assert all(len(r['processes'])==1 and r['processes'][0]['pid']==pid for r in rows)
 cpu=(rows[-1]['processes'][0]['cpuTicks']-rows[0]['processes'][0]['cpuTicks'])/os.sysconf('SC_CLK_TCK')/elapsed*100
 peak=lambda k:max(r['processes'][0]['memory'][k] for r in rows)
 gates=dict(rss=peak('Rss')<=40*1048576,pss=peak('Pss')<=40*1048576,cpu=cpu<.5,swap=peak('Swap')==0,quiet=all(r['load'][0]<=1 for r in rows),noHelpers=True)
 (work/f'new-idle-{n}-samples.json').write_text(json.dumps(rows))
 report['windows'].append(dict(index=n,elapsed=elapsed,cpuPercent=cpu,rssPeak=peak('Rss'),pssPeak=peak('Pss'),gates=gates))
 if gates['quiet']:
  if not all(gates.values()):break
  accepted+=1
 (work/'new-idle.json').write_text(json.dumps(report,indent=2));print('window',n,gates,flush=True)
 if accepted==2:break
report['passed']=accepted==2 and all(all(w['gates'].values()) for w in report['windows'] if w['gates']['quiet']);(work/'new-idle.json').write_text(json.dumps(report,indent=2))
