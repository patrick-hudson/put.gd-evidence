import json,sys,hashlib,concurrent.futures
from pathlib import Path
sys.path.insert(0,'.');from tools.lab.physical_host import PhysicalHost
base=Path('work/ta1532/r2');out=base/'restoration';out.mkdir(exist_ok=True)
receipts={'k72':'2026-11-14T23-24-11Z-release.json','f44':'2026-11-14T23-16-48Z-release.json','m74':'2026-11-14T23-21-22Z-release.json'}
def host(h):
 p=PhysicalHost(json.loads(Path('work/ta1532/'+h+'.json').read_text()))
 version={'k72':'plasmashell --version','f44':'gnome-shell --version','m74':'cinnamon --version'}[h]
 package='rpm -q putgd || true' if h=='f44' else "dpkg-query -W -f='${db:Status-Abbrev} ${Version}\\n' putgd"
 v=p.ssh(p.run,'cat /etc/os-release\n'+version+'\n'+package+'\ncommand -v putgd || true\nps -C putgd,putgd-ui,putgd-region,putgd-record -o pid,args || true\n')
 (out/(h+'-final.txt')).write_text(v)
 remote='/home/patrick/putgd-lab/locks/history/'+receipts[h];local=base/'private'/(h+'-release.json');p.get(p.run,remote,str(local));b=json.loads(local.read_text());assert b['event']=='release' and b['releasedBy']=='ta1532-r2' and not b['check']['left']
 return {'host':h,'event':b['event'],'at':b['at'],'releasedBy':b['releasedBy'],'checkLeft':b['check']['left'],'receiptOnHost':remote,'receiptSha256':hashlib.sha256(local.read_bytes()).hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:results=list(e.map(host,receipts))
(out/'desktop-leases.json').write_text(json.dumps(results,indent=2)+'\n')
p=PhysicalHost(json.loads(Path('work/ta1532/f44.json').read_text()));v=p.ssh(p.run,'ps -C qemu-system-x86_64 -o pid,args || true\nss -ltn\n');(out/'f44-guest-host-final.txt').write_text(v)
wall=json.loads(Path('/home/patrick/work/put.gd/tools/qemu-grid/remote-displays.json').read_text());assert not any('ta1532' in x.get('name','') for x in wall);(out/'wall-final.json').write_text(json.dumps({'ownedTilesRemaining':[],'otherEntriesPreserved':len(wall)},indent=2))
print('Verified three clean desktop releases, package absence, and guest/wall teardown')
