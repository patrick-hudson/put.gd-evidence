import subprocess,sys,pathlib,shlex
base=pathlib.Path('/home/patrick/work/rolling-capture-research/acceptance')
ips={'d69':'69','f44':'70','m74':'74'}
host=sys.argv[1]; opts=['-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+host+'/known_hosts'];dest='patrick@192.168.68.'+ips[host]
if sys.argv[2]=='put':sys.exit(subprocess.call(['scp']+opts+sys.argv[3:-1]+[dest+':'+sys.argv[-1]],stdin=subprocess.DEVNULL))
if sys.argv[2]=='get':sys.exit(subprocess.call(['scp']+opts+[dest+':'+sys.argv[3],sys.argv[4]],stdin=subprocess.DEVNULL))
sys.exit(subprocess.call(['ssh','-n']+opts+[dest,sys.argv[2]],stdin=subprocess.DEVNULL))
