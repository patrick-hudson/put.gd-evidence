import subprocess,sys,os
H=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/d69/known_hosts','patrick@192.168.68.69']
G=['ssh','-i','/tmp/b1364/identity','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/tmp/b1364/known_hosts','-p','22446','-o','ProxyCommand=ssh -i /home/patrick/.ssh/awskey_110724 -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/d69/known_hosts -W %h:%p patrick@192.168.68.69','lab@127.0.0.1']
if __name__=='__main__':
 r=subprocess.run((H if sys.argv[1]=='h' else G)+[sys.argv[2]])
 sys.exit(r.returncode)
