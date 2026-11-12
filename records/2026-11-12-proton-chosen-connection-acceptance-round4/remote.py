import subprocess,sys
h=sys.argv[1];ip={'d69':69,'k72':72,'m74':74,'f44':70}[h]
r=subprocess.run(['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','-o',f'UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/{h}/known_hosts',f'patrick@192.168.68.{ip}']+sys.argv[2:]);sys.exit(r.returncode)
