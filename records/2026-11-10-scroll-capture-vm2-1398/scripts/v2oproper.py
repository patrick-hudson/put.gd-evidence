from pathlib import Path
import sys,shlex,shutil
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');r=base/'repo/work/lab-runs/of';o=base/'v2evidence/o';old=o/'pre-dismiss-witnesses';old.mkdir(exist_ok=True)
for f in list(o.iterdir()):
 if f.is_file() and f.suffix in ['.png','.console']:shutil.copy2(f,old/f.name)
for name in ['cap','postcap','stop']:
 lab.guest_session(r,'python3 -c '+shlex.quote("from pathlib import Path;p=Path('/tmp/v2/cases/"+name+"');p.rename(p.with_name('pre-dismiss-"+name+"'))"))
s=(base/'v2obatch.py').read_text().replace("for i in range(1,4):case(kind+str(i)","for i in range(1,4):case(kind+'verified'+str(i)").replace("case('plain'+str(i)","case('plainverified'+str(i)")
exec(compile(s,'v2obatch-verified','exec'))
