import json,hashlib,shutil,argparse,scroll_run
from pathlib import Path
P=Path('/home/patrick/work/sa2');o=json.loads((P/'user-result.json').read_text());before={r['id'] for r in o['before']['records']};new=[r for r in o['after']['records'] if r['id'] not in before];out=P/'user';out.mkdir(exist_ok=True)
for r in new:
 f=Path(r['local']['path']);shutil.copyfile(f,out/'capture.png')
result={'newRecords':new,'pass':len(new)==1 and new[0]['sha256']=='d8cf2f220f1fe621989e0c7d36d056cb93ca25384d7759be8b400eb82fad5d1f' and new[0]['uploadStatus']=='uploaded','expectedSha256':'d8cf2f220f1fe621989e0c7d36d056cb93ca25384d7759be8b400eb82fad5d1f'}
a=argparse.Namespace(scale=1,height=2400,rows=60,first_pixel=0,header=0,footer=0,code_width=960,format='fixture',scrollbar=0)
result['verification']=scroll_run.verify(out/'capture.png',a)
result['pass']=len(new)==1 and new[0]['uploadStatus']=='uploaded' and result['verification']['pass']
(out/'result.json').write_text(json.dumps(result,indent=2));print(result['pass'],len(new))
