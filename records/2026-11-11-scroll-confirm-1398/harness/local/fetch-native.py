from control import *
import tarfile,hashlib
h=sys.argv[1];root=sys.argv[2];label=sys.argv[3] if len(sys.argv)>3 else h;p=BASE/'native'/label;p.mkdir(parents=True,exist_ok=True)
opts=['-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+h+'/known_hosts']
subprocess.run(['scp',*opts,'patrick@192.168.68.'+IPS[h]+':/home/patrick/work/'+root+'/export-confirm.tgz',str(p/'export-confirm.tgz')],check=True)
q=p/'raw';q.mkdir();tarfile.open(p/'export-confirm.tgz').extractall(q,filter='data');m=json.loads((q/'hashes-confirm.json').read_text());assert all(hashlib.sha256((q/n).read_bytes()).hexdigest()==s for n,s in m.items());(p/'workstation-verified.json').write_text(json.dumps({'verified':True,'files':len(m),'archiveSha256':hashlib.sha256((p/'export-confirm.tgz').read_bytes()).hexdigest()},indent=2));print(label,'verified',len(m))
