import sys,json,shlex
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');k=sys.argv[1];r=base/'repo/work/lab-runs'/(k+'f');o=base/'v2evidence'/k
h=json.loads((o/'user-final-history.json').read_text());record=h['records'][0]
code="""import json,shutil,hashlib
from pathlib import Path
record=json.loads(%r);f=Path(record['local']['path']);assert hashlib.sha256(f.read_bytes()).hexdigest()==record['sha256'];d=Path('/tmp/v2/cases/user');d.mkdir(exist_ok=True);shutil.copyfile(f,d/'capture.png');(d/'result.json').write_text(json.dumps({'history':record,'capture':{'state':'done','endReason':'user-capture','result':{'sha256':record['sha256']}}},indent=2))
""" % json.dumps(record)
print(lab.guest_session(r,'python3 -c '+shlex.quote(code)))
