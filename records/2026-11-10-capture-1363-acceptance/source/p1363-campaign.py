import subprocess,json,os,sys,fcntl,tempfile,socket,time,shlex
from pathlib import Path
S=Path('/home/patrick/work/putgd-evidence/2026-11-09-features/acceptance-1363')
OUT=Path('/home/patrick/work/putgd-evidence/2026-11-09-features/acceptance-worker-1363');OUT.mkdir(exist_ok=True)
HOSTS={'m74':'74','k72':'72','d69':'69','f44':'70'}
def ssh(h):return ['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+h+'/known_hosts','patrick@192.168.68.'+HOSTS[h]]
def remote(h,cmd,**kw):return subprocess.run(ssh(h)+[cmd],check=True,text=True,**kw)
PROFILES={
 'cinnamon':('m74','ac5','cinnamon-x11-appimage','transfer-1e7496436875',22220,22579,247,'m74','known_hosts',6088),
 'gnome':('m74','fg3','fedora-gnome-wayland','transfer-deps31-fedora-fb83af6d',22238,22575,239,'m74',None,6080),
 'kde':('k72','ak4','kde-wayland','nightly-kde-49fcacff969b',22234,22576,241,'k72',None,6082),
 'budgie':('d69','ab2','fedora45-budgie','fedora45-budgie',22442,22577,243,'d69',None,6084),
 'hyprland':('d69','ah5','omarchy-hyprland','omarchy-hyprland-20261108',22440,22578,245,'omarchy',None,6086)}

def launch(d):
 h,r,p,g,pin,port,vnc,k,known,wall=PROFILES[d];gold='/home/patrick/work/put.gd/work/lab-images/'+g;key='/home/patrick/work/put.gd/work/lab-bootstrap-'+k+'/identity'
 probe_code='import socket; ports='+repr([port,5900+vnc,5901+vnc])+'; sockets=[]\nfor p in ports:\n s=socket.socket();s.bind(("127.0.0.1",p));sockets.append(s)\nprint("remote ports available",ports)'
 remote(h,shlex.join(['python3','-c',probe_code]))
 for local_port in [wall,wall+1]:
  with socket.socket() as probe:probe.bind(('127.0.0.1',local_port))
 cmd='cd ~/work/i1363; python3 tools/diagnostics/check_socket_paths.py --socket /home/patrick/work/i1363/work/lab-runs/'+r+'/qmp.sock /run/user/1000/putgd/session.sock; test ! -e work/lab-runs/'+r+'; ss -ltn'
 capacity=remote(h,'free -m; uptime; df -h /home; test -r /dev/kvm -a -w /dev/kvm',capture_output=True)
 (OUT/'transport').mkdir(exist_ok=True);(OUT/'transport'/(r+'-capacity.txt')).write_text(capacity.stdout)
 remote(h,cmd)
 env=('KNOWN_HOSTS=/home/patrick/work/put.gd/work/lab-bootstrap-'+k+'/'+known+' ') if known else ''
 unit='putgd-vm-1363acc-'+r
 subprocess.run(['systemd-run','--user','--unit='+unit,'--collect','--property=Type=exec','--property=Restart=on-failure','--property=RestartSec=3s',*ssh(h)[:-1],'-NT','-o','ExitOnForwardFailure=yes','-L',f'127.0.0.1:{wall}:127.0.0.1:{5900+vnc}','-L',f'127.0.0.1:{wall+1}:127.0.0.1:{5901+vnc}',ssh(h)[-1]],check=True)
 for _ in range(50):
  result=subprocess.run(['systemctl','--user','show','--property=MainPID','--value',unit],capture_output=True,text=True)
  try:
   tunnel_pid=int(result.stdout.strip());args=Path('/proc/'+str(tunnel_pid)+'/cmdline').read_bytes().split(b'\0')
   matched=all(f'127.0.0.1:{wall+i}:127.0.0.1:{5900+vnc+i}'.encode() in args for i in range(2))
   bound=[]
   for lp in [wall,wall+1]:
    with socket.socket() as probe:
     try:probe.bind(('127.0.0.1',lp));bound.append(False)
     except OSError:bound.append(True)
   if matched and all(bound):break
  except (ValueError,OSError):pass
  time.sleep(.2)
 else:
  subprocess.run(['systemctl','--user','stop',unit]);raise RuntimeError('Owned wall tunnel did not bind both verified ports; VM not started')
 (OUT/'transport').mkdir(exist_ok=True);(OUT/'transport'/(r+'.json')).write_text(json.dumps({'run':r,'unit':unit,'pid':tunnel_pid,'localPorts':[wall,wall+1],'remotePorts':[5900+vnc,5901+vnc],'argvMappingsVerified':True},indent=2))
 path=Path('/home/patrick/work/put.gd/tools/qemu-grid/remote-displays.json')
 with open('/tmp/p1363-wall.lock','w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX); rows=json.loads(path.read_text());rows += [{'name':f'1363 acceptance {d} {r}','port':wall+i,'type':'vm','hostIp':'192.168.68.'+HOSTS[h],'group':'1363acc-'+r,'head':i} for i in range(2)]
  fd,tmp=tempfile.mkstemp(dir=path.parent);os.write(fd,(json.dumps(rows,indent=1)+'\n').encode());os.close(fd);os.chmod(tmp,0o664);os.replace(tmp,path)
 remote(h,env+'sh /tmp/p1363-vm-launch.sh '+f'{r} {p} {gold} {pin} {port} {vnc} {key} 1280x800+0+0,1024x768+1280+0')
 print('launched',d,r,flush=True)
if __name__=='__main__':launch(sys.argv[1])
