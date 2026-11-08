import json,sys,subprocess,shlex,datetime,os
from pathlib import Path
host,run,profile,golden,port,vnc,wall=sys.argv[1:];port=int(port);vnc=int(vnc);wall=int(wall)
base=Path('/home/patrick/work/put.gd');ip={'f44':'192.168.68.70','d69':'192.168.68.69'}[host]
ssh=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(base/'work/remote-builders'/host/'known_hosts'),'patrick@'+ip]
root='/home/patrick/work/np1275';key='/home/patrick/work/put.gd/work/'+('lab-bootstrap-omarchy/identity' if 'omarchy' in profile else 'lab-bootstrap-f44/identity' if host=='f44' else 'lab-bootstrap-d69/rec-ws/identity')
code="from pathlib import Path\nimport re\np=Path('/home/patrick/work/put.gd/work/lab-images/"+golden+"/known_hosts')\ns=p.read_text();s=re.sub(r'\\[127\\.0\\.0\\.1\\]:[0-9]+','[127.0.0.1]:"+str(port)+"',s);t=Path('work/sp');t.mkdir(mode=0o700,exist_ok=True);(t/'"+run+"-known_hosts').write_text(s)\n"
cmd='cd '+root+' && python3 -c '+shlex.quote(code)+' && python3 tools/lab/lab.py launch --profile '+profile+' --golden /home/patrick/work/put.gd/work/lab-images/'+golden+'/image.qcow2 --run work/lab-runs/'+run+' --bootstrap-key '+key+' --known-hosts work/sp/'+run+'-known_hosts --ssh-port '+str(port)+' --vnc-display '+str(vnc)
r=subprocess.run(ssh+[cmd],capture_output=True,text=True);Path('work/sp1275/'+run+'-launch.log').write_text(r.stdout+r.stderr)
assert r.returncode==0,(r.stdout+r.stderr)[-1500:]
unit='putgd-vm-sp1275-'+run
subprocess.run(['systemd-run','--user','--unit='+unit,'--collect','--property=Restart=on-failure',*ssh[:-1],'-N','-T','-o','ExitOnForwardFailure=yes','-o','ServerAliveInterval=30','-L',f'127.0.0.1:{wall}:127.0.0.1:{5900+vnc}',ssh[-1]],check=True)
p=base/'tools/qemu-grid/remote-displays.json';old=p.read_bytes();entries=json.loads(old);assert all(e['port']!=wall for e in entries)
backup=base/'work/wall-backups';backup.mkdir(exist_ok=True);(backup/('sp1275-'+run+'-'+datetime.datetime.now().strftime('%H%M%S')+'.json')).write_bytes(old)
entries.append(dict(name=f'SP1275 {host} {profile} {run}',port=wall,type='vm'));tmp=p.with_suffix('.sp1275.tmp');tmp.write_text(json.dumps(entries,indent=2)+'\n');os.replace(tmp,p)
print(json.dumps(dict(run=run,host=host,wall=wall,unit=unit)))
