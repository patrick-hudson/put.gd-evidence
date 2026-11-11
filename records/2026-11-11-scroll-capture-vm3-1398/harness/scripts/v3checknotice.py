import sys,json,re
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
ns={};exec((B/'v2analyze.py').read_text().split('out=json.loads')[0],ns)
r=B/'repo/work/lab-runs/o3';o=B/'v3evidence/o'
for n,exp in [('cap-local',2000),('postcap-local',2400)]:
 d=o/'peek'/n;d.mkdir(exist_ok=True)
 for f in ['capture.png','result.json','helper.log']:lab.get(r,'/tmp/v3/cases/'+n+'/'+f,d/f)
 a=json.loads((d/'result.json').read_text());v=ns['ruler'](d/'capture.png',exp,codewidth=1280);(d/'verification.json').write_text(json.dumps(v,indent=2));print(n,a['capture']['endReason'],v,re.findall(r'scroll: source[^\n]*',(d/'helper.log').read_text()))
print((o/'notification-bus.log').read_text()[-4500:])
