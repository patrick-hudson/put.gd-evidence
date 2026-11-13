from pathlib import Path
import sys,json,subprocess,socket,os,fcntl
name,action=sys.argv[1:3];assert name.startswith('f') and name.isalnum();port=int(sys.argv[3]);remoteport=int(sys.argv[4]);label=sys.argv[5];unit='putgd-vm-b1428-'+name
cfg=Path('/home/patrick/work/put.gd/tools/qemu-grid/remote-displays.json');guard=Path('/tmp/b1428/wall-config.lock')
with guard.open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);data=json.loads(cfg.read_text())
 if action=='add':
  assert not any(x['port']==port for x in data)
  with socket.socket() as s:s.bind(('127.0.0.1',port))
  subprocess.run(['systemd-run','--user','--unit='+unit,'--collect','--property=Type=exec','--property=Restart=on-failure','--property=RestartSec=3s','/usr/bin/ssh','-NT','-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/f44/known_hosts','-o','ExitOnForwardFailure=yes','-o','ServerAliveInterval=30','-o','ServerAliveCountMax=3','-L',f'127.0.0.1:{port}:127.0.0.1:{remoteport}','patrick@192.168.68.70'],check=True)
  data.append({'name':label,'port':port,'type':'vm','hostIp':'192.168.68.70'})
 elif action=='remove':
  own=[x for x in data if x.get('port')==port and x.get('name')==label];assert len(own)==1
  data=[x for x in data if x not in own];subprocess.run(['systemctl','--user','stop',unit+'.service'],check=True)
 else:raise ValueError(action)
 temp=cfg.with_name('remote-displays.b1428-'+name+'.tmp');assert not temp.exists();temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(cfg)
 print(json.dumps({'action':action,'unit':unit,'entry':{'name':label,'port':port},'remotePort':remoteport,'remaining':len(data)}))
