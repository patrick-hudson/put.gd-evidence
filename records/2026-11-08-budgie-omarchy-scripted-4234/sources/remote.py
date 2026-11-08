import sys,subprocess
host=sys.argv[1];ip={'f44':'192.168.68.70','d69':'192.168.68.69'}[host]
r=subprocess.run(['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+host+'/known_hosts','patrick@'+ip,*sys.argv[2:]])
sys.exit(r.returncode)
