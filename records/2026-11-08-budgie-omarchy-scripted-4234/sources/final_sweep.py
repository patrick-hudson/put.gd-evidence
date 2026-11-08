import json,os,re,subprocess,sys,shlex
from pathlib import Path
host=sys.argv[1];ip='192.168.68.'+('70' if host=='f44' else '69');opts=['-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+host+'/known_hosts']
code='''import json,os,re
from pathlib import Path
from tools.lab.desktop_lock import Desktop
root=Path('/home/patrick/work/np1275');vms=[];alive=[]
for run in (root/'work/lab-runs').glob('sp[1-5]'):
 p=run/'state.json'
 if not p.exists():continue
 v=json.loads(p.read_text());proc=Path('/proc')/str(v['pid']);owned=False
 try:owned=str(run/'disk.qcow2').encode() in (proc/'cmdline').read_bytes()
 except OSError:pass
 vms.append(dict(run=run.name,id=v['id'],pid=v['pid'],ownedQemuAlive=owned,overlayExists=(run/'disk.qcow2').exists()))
for p in Path('/proc').glob('[0-9]*'):
 try:
  if int(p.name)==os.getpid() or p.stat().st_uid!=os.getuid():continue
  args=(p/'cmdline').read_bytes().split(b'\\0');cwd=Path(os.readlink(p/'cwd'));comm=(p/'comm').read_text().strip()
  owned=(comm.startswith(('qemu','putgd')) and any(str(root).encode()+b'/' in a for a in args)) or (cwd==root and comm.startswith('python') and any(b'tools.lab.surface_driver.run' in a or b'work/sp/pass.py' in a or b'work/sp/live_run.py' in a or b'work/sp/fm.py' in a for a in args))
  if owned:alive.append(dict(pid=int(p.name),comm=comm,cwd=str(cwd)))
 except (OSError,ValueError):pass
slot=Path.home()/'putgd-lab/locks/tier1-guest.lock.d';owner=json.loads((slot/'owner.json').read_text()) if (slot/'owner.json').exists() else {};ours=str(owner.get('session','')).startswith('sp1275-')
proton=Desktop(Path.home()/'putgd-lab/locks',HOST,resource='proton').status();our_proton=proton['state']!='free' and 'sp1275' in json.dumps(proton)
out=dict(host=HOST,vms=vms,ownedProcessesAlive=alive,guestSlotExists=slot.exists(),guestSlotOwnedByCampaign=ours,protonResourceState=proton['state'],protonResourceHeldByCampaign=our_proton)
assert not alive and not ours and not our_proton and all(not v['ownedQemuAlive'] and not v['overlayExists'] for v in vms)
print(json.dumps(out,indent=2))
'''.replace('HOST',repr(host))
cmd='cd /home/patrick/work/np1275 && python3 -c '+shlex.quote(code)
text=subprocess.check_output(['ssh','-n',*opts,'patrick@'+ip,cmd],text=True)
root=Path('work/sp1275/cleanup');root.mkdir(parents=True,exist_ok=True);(root/(host+'-sweep.json')).write_text(text);print('verified campaign cleanup on',host)
