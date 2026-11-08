import json,subprocess,sys,datetime
from pathlib import Path
rows=[('sp1','f44','fedora45-budgie','AppImage'),('sp3','d69','fedora44-budgie','RPM'),('sp4','f44','ubuntu-budgie-2604','DEB'),('sp2','d69','omarchy-hyprland-20261108','Arch'),('sp5','d69','omarchy-hyprland-20261108','AppImage')]
sys.path.insert(0,str(Path.cwd()));from tools.lab.nightly_desktops import FLOWS
result=[]
for run,host,desktop,pkg in rows:
 code="from pathlib import Path\nimport json\nr=Path('/home/patrick/work/np1275/work/sp');out=[]\nfor p in sorted(r.glob('"+run+"-*/cells.json'),key=lambda p:p.stat().st_mtime_ns):\n out.append(dict(path=str(p),cells=json.loads(p.read_text())))\nprint(json.dumps(out))"
 import shlex
 p=subprocess.run([sys.executable,'work/sp1275/remote.py',host,'python3 -c '+shlex.quote(code)],capture_output=True,text=True,check=True)
 attempts=json.loads(p.stdout);cells={k:dict(status='not_run',cause='pending') for k in FLOWS}
 for a in attempts:
  for k,v in a['cells'].items():
   if v['status']=='not_run' and cells[k]['status']!='not_run':continue
   cells[k]=dict(v,attempt=a['path'])
 result.append(dict(run=run,host=host,desktop=desktop,package=pkg,cells=cells))
Path('work/sp1275/progress.json').write_text(json.dumps(result,indent=2))
lines=['# Scripted outcome pass — v26.1108.4234-nightly','', '| Row / package | '+' | '.join(FLOWS.values())+' | Pass / fail / not-run | Total |','|---|'+'---|'*(len(FLOWS)+2)]
for r in result:
 cells=r['cells'];counts={s:sum(v['status']==s for v in cells.values()) for s in ('pass','fail','not_run')}
 lines.append('| '+r['desktop']+' / '+r['package']+' | '+' | '.join((cells[k]['status'].replace('_','-')+('*' if k=='survives_exit' and cells[k].get('proof',{}).get('persistenceSetup') else '†' if k=='window_desktop' and cells[k].get('proof',{}).get('window')=='documented unavailable' else '')) for k in FLOWS)+' | '+str(counts['pass'])+' / '+str(counts['fail'])+' / '+str(counts['not_run'])+' | 13 |')
lines+=['','Updated '+datetime.datetime.now(datetime.timezone.utc).isoformat()+'. These are scripted outcome results, not Tier1 driver cells. All rows use the exact published tag and clean source 2b5e1b2d3. Earlier script failures remain in evidence; the table uses the latest completed observation per outcome.','', 'Current campaign started19:46UTC; fresh owned overlays sp1/sp2/sp3/sp4/sp5 on wall6040/6041/6042/6045/6044. Port6043 belongs to the GNOME worker and was preserved; our attempted tunnel bind failed closed, then moved to6045. No chart/timer/builder-nightly-config changes, no issues, no EC2, no physical lock. GNOME worker VMs untouched. #1314 remains at c155c3ec855aa69bdb7b49b07081847fe013af65.','', 'Window/desktop pass† means desktop pixels matched exactly and window capture reported window_unavailable with the documented missing ext-foreign-toplevel-image-capture-source protocol reason (labwc0.9, Fedora44/Ubuntu26). Exit pass* means a VM setup correction was required: distro clipman (Budgie) or wl-clip-persist (Omarchy), owned only for that cell with tmpfs storage. The unchanged stock goldens fail this outcome: ordinary wl-copy and put.gd both lose text on owner exit without a clipboard manager. Original failures and controls remain in evidence; no product lifetime change is implied. All other outcomes use the golden desktop plus standard suite probes.','','<!-- SCRIPTED_PROGRESS_END -->','']
p=Path('/home/patrick/work/put.gd/work/desktop-expansion-1275/reports/nightly-pass-budgie-omarchy.md');old=p.read_text()
if '<!-- SCRIPTED_PROGRESS_END -->' in old:old=old.split('<!-- SCRIPTED_PROGRESS_END -->',1)[1].lstrip()
else:old=old[old.index('## Previous Tier 1 driver campaign'):]
p.write_text('\n'.join(lines)+old)
for r in result:print(r['run'],{s:sum(v['status']==s for v in r['cells'].values()) for s in ('pass','fail','not_run')})
