import sys,json
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
ns={};exec((B/'v2analyze.py').read_text().split('out=json.loads')[0],ns)
k=sys.argv[1];r=B/'repo/work/lab-runs'/(k+'3');o=B/'v3evidence'/k/'peek';o.mkdir(exist_ok=True)
for i in range(1,6):
 n='clean%02d'%i;d=o/n;d.mkdir(exist_ok=True)
 for f in ['capture.png','result.json','helper.log']:lab.get(r,'/tmp/v3/cases/'+n+'/'+f,d/f)
 print(k,n,ns['ruler'](d/'capture.png',2400,codewidth=1280),flush=True)
