from control import *
import shlex
out={}
for h in IPS:
 roots=['/home/patrick/work/pcn']+(['/home/patrick/work/pc2'] if h=='f44' else ['/home/patrick/work/pwc'] if h=='m74' else [])
 code="""from pathlib import Path
import json,subprocess
roots=%r
left=[]
for p in Path('/proc').iterdir():
 if not p.name.isdecimal():continue
 try:
  env=(p/'environ').read_bytes().split(b'\\0')
  if any(('XDG_CONFIG_HOME='+r+'/c').encode() in env for r in roots):left.append({'pid':int(p.name),'comm':(p/'comm').read_text().strip()})
 except OSError:pass
q=subprocess.run(%r,capture_output=True,text=True)
print(json.dumps({'ownedProfileProcesses':left,'putgdPackageInstalled':q.returncode==0,'packageQuery':q.stdout.strip()}))
"""%(roots,['rpm','-q','putgd'] if h=='f44' else ['dpkg-query','-W','-f=${db:Status-Status}','putgd'])
 r=json.loads(ssh(h,'python3 -c '+shlex.quote(code),check=True,capture_output=True,text=True).stdout)
 if h!='f44':r['putgdPackageInstalled']=r['packageQuery']=='installed'
 assert not r['ownedProfileProcesses'] and not r['putgdPackageInstalled'],r;out[h]=r
code="""from pathlib import Path
import json
b=Path('/home/patrick/work/svm1398/repo/work/lab-runs');out={}
for k in ['ocn','bcn','ncn','kcn','kcr2']:
 p=b/k;s=json.loads((p/'state.json').read_text());out[k]={'pid':s['pid'],'pidExists':Path('/proc/'+str(s['pid'])).exists(),'overlayExists':(p/'disk.qcow2').exists(),'goldenExists':Path(s['golden']).is_file()}
print(json.dumps(out))
"""
v=json.loads(ssh('d69','python3 -c '+shlex.quote(code),check=True,capture_output=True,text=True).stdout);assert all(not x['pidExists'] and not x['overlayExists'] and x['goldenExists'] for x in v.values());out['guests']=v
wall=json.loads(Path('/home/patrick/work/put.gd/tools/qemu-grid/remote-displays.json').read_text());before=json.loads((BASE/'wall-before.json').read_text());assert all(x in wall for x in before);assert not any(x.get('name','').startswith('Scroll confirm eaa1ba198') for x in wall);out['wall']=wall
out['tunnels']={n:subprocess.run(['systemctl','--user','is-active','putgd-vm-scn-'+n],capture_output=True,text=True).stdout.strip() for n in ['ocn','bcn','ncn','kcn']};assert all(x!='active' for x in out['tunnels'].values());(BASE/'final-cleanup.json').write_text(json.dumps(out,indent=2));print('All owned test processes, packages, VM disks, tunnels and wall entries cleaned; original physical tiles preserved.')
