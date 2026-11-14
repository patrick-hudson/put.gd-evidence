from pathlib import Path
import json,datetime
result=[]
for run in ('w34m3','w7m2','w34m5','w34m6'):
 root=Path('/tmp')/run;events=[];errors=[]
 for p in (root/'profile/state/putgd/logs').glob('*.jsonl'):
  for l in p.read_text().splitlines():
   r=json.loads(l)
   if r.get('category')=='putgd.ui' and r.get('message') in ('Helper started','Helper exited','Killing helper','Helper killing','Helper failed to start'):events.append(r)
   if 'ui_unavailable' in l or 'ui_incompatible' in l:errors.append(r)
 frames={}
 for name in ('history.png','history-before-close.png'):
  p=root/name
  if p.exists():frames[name]=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()
 result.append({'run':run,'uiProcessEvents':events,'uiUnavailableOrIncompatibleLines':errors,'frameMtimesUtc':frames})
(Path.home()/'work/w7-34/ui-historical.json').write_text(json.dumps(result,indent=2)+'\n')
