import subprocess,sys
hosts={'f44':'70','k72':'72','aurora-amd':'71'}
h=sys.argv[1]
args=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+h+'/known_hosts','patrick@192.168.68.'+hosts[h]]
if sys.argv[2]=='--copy':
 args[0]='scp';args+=sys.argv[3:-1]+[args.pop() + ':'+sys.argv[-1]]
elif sys.argv[2]=='--get':
 args[0]='scp';host=args.pop();args+=[host+':'+sys.argv[3],sys.argv[4]]
else: args+=sys.argv[2:]
sys.exit(subprocess.run(args).returncode)
