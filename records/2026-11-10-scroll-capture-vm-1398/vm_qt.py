import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'repo/tools/lab'));import lab
r=Path('/home/patrick/work/svm1398/repo/work/lab-runs')/sys.argv[1]
s='''python3 - <<'INNER'
import os,signal,subprocess,shutil,json
from pathlib import Path
p=Path.home()/'putgd-lab';pid=int((p/'gtk.pid').read_text());os.kill(pid,signal.SIGTERM)
f=p/'native-qt.txt';f.write_text('\\n'.join('Row %04d — native Qt acceptance' % i for i in range(1500)))
a=['kate','--new',str(f)] if shutil.which('kate') else ['python3',str(p/'toolkit.py'),'qt']
fout=open(p/'qt.log','w');q=subprocess.Popen(a,stdout=fout,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True);(p/'qt.pid').write_text(str(q.pid));print(a,q.pid)
INNER'''
print(lab.guest_session(r,s))
