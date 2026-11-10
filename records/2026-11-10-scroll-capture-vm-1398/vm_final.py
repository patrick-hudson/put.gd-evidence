import sys,json,shlex,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'repo/tools/lab'));import lab
r=sys.argv[1];run=Path('/home/patrick/work/svm1398/repo/work/lab-runs')/r
s='''python3 - <<'INNER'
from pathlib import Path
import os,json,hashlib,subprocess,time
out={'time':time.time(),'host':os.uname().nodename,'uname':list(os.uname()),'processes':[],'stagingFiles':[]}
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  exe=p.joinpath('exe').resolve()
  if exe.name in ['putgd','putgd-record','putgd-ui','putgd-capture','putgd-region','putgd-clipboard-keeper']:
   out['processes'].append({'pid':int(p.name),'exe':str(exe),'sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'memory':p.joinpath('smaps_rollup').read_text()})
 except:pass
p=Path.home()/'putgd-lab/data'
for d in p.rglob('scroll'):
 out['stagingFiles'] += [str(f) for f in d.rglob('*') if f.is_file()]
for args in [['kwin_wayland','--version'],['rpm','-q','budgie-desktop','labwc'],['pacman','-Q','hyprland','omarchy'],['loginctl','list-sessions']]:
 try:out[' '.join(args)]=subprocess.check_output(args,stderr=subprocess.STDOUT,text=True)
 except Exception as e:out[' '.join(args)]=str(e)
print(json.dumps(out))
INNER'''
(run/'final-identity.json').write_text(lab.guest_session(run,s));print(r,'recorded')
