#!/usr/bin/env python3
import subprocess,sys
host=sys.argv[1]; ip={'m74':74,'f44':70,'d69':69,'k72':72,'aurora-amd':71}[host]
args=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o',f'UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/{host}/known_hosts',f'patrick@192.168.68.{ip}']
subprocess.run(args+[sys.argv[2]],check=True)
