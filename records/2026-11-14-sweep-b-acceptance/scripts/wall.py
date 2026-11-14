import sys,subprocess,json,pathlib,fcntl,os
act,name=sys.argv[1:];local,remote={'b3':(6071,6011),'b4':(6071,6011),'b5':(6071,6011),'h3':(6073,6013),'h4':(6073,6013),'h5':(6073,6013),'h6':(6077,6017),'h7':(6081,6021),'ha1':(6079,6019),'p2':(6075,6015),'p3':(6083,6023)}[name];unit='putgd-sb-'+name
if act=='up':subprocess.run(['systemd-run','--user','--unit='+unit,'--collect','--property=Type=exec','/usr/bin/ssh','-NT','-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/f44/known_hosts','-o','ExitOnForwardFailure=yes','-L',f'127.0.0.1:{local}:127.0.0.1:{remote}','-L',f'127.0.0.1:{local+1}:127.0.0.1:{remote+1}','patrick@192.168.68.70'],check=True)
p=pathlib.Path('/home/patrick/work/put.gd/tools/qemu-grid/remote-displays.json')
with open(str(p)+'.lock','a') as f:
 fcntl.flock(f,fcntl.LOCK_EX);v=[x for x in json.loads(p.read_text()) if x.get('group')!='sweep-b-'+name]
 if act=='up':
  assert not any(x.get('port') in (local,local+1) for x in v)
  v.extend({'name':'Sweep B '+name+' - two heads','port':local+h,'group':'sweep-b-'+name,'head':h,'type':'vm','hostIp':'192.168.68.70'} for h in (0,1))
 q=p.with_suffix('.sb.tmp');q.write_text(json.dumps(v,indent=2));os.replace(q,p)
if act=='down':subprocess.run(['systemctl','--user','stop',unit+'.service'],check=True)
