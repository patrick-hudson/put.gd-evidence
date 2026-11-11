from pathlib import Path
import sys,shlex,time,shutil
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');r=base/'repo/work/lab-runs/of';o=base/'v2evidence/o';old=o/'preclean-witnesses';old.mkdir(exist_ok=True)
for f in list(o.iterdir()):
 if f.is_file() and f.suffix in ['.png','.console']:shutil.copy2(f,old/f.name)
script='\n'.join(f'gdbus call --session -d org.freedesktop.Notifications -o /org/freedesktop/Notifications -m org.freedesktop.Notifications.CloseNotification {i} >/dev/null' for i in range(1,20))
print(lab.guest_session(r,script),flush=True)
for name in ['cap','postcap','stop']:
 print(lab.guest_session(r,'python3 -c '+shlex.quote("from pathlib import Path;p=Path('/tmp/v2/cases/"+name+"');p.rename(p.with_name('preclean-"+name+"'))")),flush=True)
s=(base/'v2obatch.py').read_text()
s=s.replace("for i in range(1,4):case(kind+str(i)","for i in range(1,4):case(kind+'clean'+str(i)")
s=s.replace("case('plain'+str(i)","case('plainclean'+str(i)")
exec(compile(s,'v2obatch-clean','exec'))
