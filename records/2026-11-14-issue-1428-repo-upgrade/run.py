import subprocess,sys,pathlib
host=sys.argv[1]; name=sys.argv[2]; command=sys.argv[3]
ip={'d69':'69','f44':'70'}[host]
a=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o',f'UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/{host}/known_hosts',f'patrick@192.168.68.{ip}',command]
p=subprocess.run(a,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
pathlib.Path(f'work/repo1428/{name}.txt').write_text('$ '+command+'\n'+p.stdout+'\nexit='+str(p.returncode)+'\n');print(p.stdout);sys.exit(p.returncode)
