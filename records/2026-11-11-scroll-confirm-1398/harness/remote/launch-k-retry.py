from pathlib import Path
import sys,json,time
repo=Path('/home/patrick/work/svm1398/repo');sys.path.insert(0,str(repo/'tools/lab'));import lab
s=json.loads((repo/'work/lab-runs/kf/state.json').read_text());r=repo/'work/lab-runs/kcr2';assert not r.exists()
for n in ['qmp.sock','vnc.sock']:assert len(str(r/n).encode())<=107
original=lab.guest_preflight
def after_desktop_boot(*args,**kwargs):
 time.sleep(25)
 return original(*args,**kwargs)
lab.guest_preflight=after_desktop_boot
sys.argv=['lab.py','launch','--profile',s['profile'],'--golden',s['golden'],'--run',str(r),'--bootstrap-key',s['bootstrap_key'],'--known-hosts',s['known_hosts'],'--ssh-port',str(s['ssh_port']),'--vnc-display',str(s['vnc_display']),'--timeout','300']
lab.main()
