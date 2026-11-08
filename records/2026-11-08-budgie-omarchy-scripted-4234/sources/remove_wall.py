import sys,json,subprocess,datetime,os,hashlib
from pathlib import Path
run,port=sys.argv[1],int(sys.argv[2]);base=Path('/home/patrick/work/put.gd');p=base/'tools/qemu-grid/remote-displays.json';old=p.read_bytes();entries=json.loads(old);owned=[e for e in entries if e['port']==port and e['name'].startswith('SP1275 ') and e['name'].endswith(' '+run)];assert len(owned)==1
new=[e for e in entries if e not in owned];stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');(base/'work/wall-backups'/('sp1275-'+run+'-retire-'+stamp+'.json')).write_bytes(old);temp=p.with_suffix('.sp1275.tmp');temp.write_text(json.dumps(new,indent=2)+'\n');os.replace(temp,p)
subprocess.run(['systemctl','--user','stop','putgd-vm-sp1275-'+run+'.service'],check=True)
receipt=dict(run=run,removed=owned,time=stamp,preserved=new,beforeSha256=hashlib.sha256(old).hexdigest(),afterSha256=hashlib.sha256(p.read_bytes()).hexdigest());Path('work/sp1275/'+run+'-wall-retirement.json').write_text(json.dumps(receipt,indent=2));print('removed owned wall tile and tunnel',run,port)
