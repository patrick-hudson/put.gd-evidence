from pathlib import Path
import json,shutil
from PIL import Image
P=Path.cwd()
for d in(P/'runs').iterdir():
 f=d/'blank-default-results.json'
 if not f.exists():continue
 rows=json.loads(f.read_text());v={r['label']:r['value']for r in rows};end=v['end'];fixture=v['fixture'];g=v['reference-geometry'];rect=end['rect'];crop=[rect[0]-int(g['x']),rect[1]-int(g['y']),rect[0]-int(g['x'])+rect[2],g['docHeight']]
 shutil.copyfile(d/'blank-default-capture.png',d/'capture.png');im=Image.open(d/'blank-default-reference.png');im.crop(crop).save(d/'reference.png')
 last=[r['value']for r in rows if r['label'].startswith('wheel-')][-1]
 result={'name':d.name,'site':'blank','mode':'user','browser':'firefox','rect':rect,'capture':end,'seconds':end['elapsedMs']/1000,'before':{'docHeight':fixture['doc']},'after':v['after-geometry'],'referenceCrop':crop,'fixture':fixture,'crossedToEnd':last['scrollY']+fixture['viewport']>=fixture['doc']-2,'pastGap':v['past-blank']}
 (d/'result.json').write_text(json.dumps(result,indent=1));print(d.name,end['endReason'],end.get('recovered'),result['crossedToEnd'])
