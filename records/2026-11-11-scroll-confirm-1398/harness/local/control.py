import subprocess,sys,json
from pathlib import Path
BASE=Path(__file__).parent
IPS={'d69':'69','f44':'70','m74':'74'}
def ssh(h,c,**kw):
 return subprocess.run(['ssh','-n','-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+h+'/known_hosts','patrick@192.168.68.'+IPS[h],c],**kw)
def put(h,src,dest):
 return subprocess.run(['scp','-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+h+'/known_hosts',str(src),'patrick@192.168.68.'+IPS[h]+':'+dest],check=True)
if __name__=='__main__':sys.exit(ssh(sys.argv[1],sys.argv[2]).returncode)
