from pathlib import Path
import subprocess as s
b=Path('/tmp/p4a');host='k72';sid='p1414-r4-k72-cleanup';lock=['python3',str(b/'desktop_lock.py')];ssh=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/k72/known_hosts','patrick@192.168.68.72']
def lease(action,res):s.run(lock+[action,host,'--resource',res,'--session',sid]+(['--owner','proton-round4','--purpose','two exact test-link cleanup actions; /tmp/p4a','--minutes','15'] if action=='acquire' else ['--verified-clean'] if action=='release' else []),check=True)
lease('acquire','desktop')
try:lease('acquire','proton')
except:lease('release','desktop');raise
try:
 s.run(['scp','-q']+ssh[1:-1]+[str(b/'cleanup4.py'),ssh[-1]+':work/p4a/'],check=True)
 s.run(ssh+['cd ~/work/p4a && python3 cleanup4.py'],check=True)
 with (b/'new/k72/diag3.tar').open('wb') as f:s.run(ssh+['cd ~/work/p4a && tar --exclude=config --exclude=data --exclude=cache -cf - diag3'],stdout=f,check=True)
 s.run(['tar','-xf',str(b/'new/k72/diag3.tar'),'-C',str(b/'new/k72')],check=True)
finally:
 lease('release','proton');lease('release','desktop')
