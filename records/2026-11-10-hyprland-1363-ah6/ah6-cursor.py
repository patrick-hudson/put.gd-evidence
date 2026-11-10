import sys,json,time
from pathlib import Path
sys.argv=['checks','ah6','/home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity','hyprland']
exec(compile(Path('/tmp/p1363-checks.py').read_text().split('build = cli(')[0],'<driver>','exec'))
E=Path(ROOT)/'work/acceptance-1363/ah6';rows=[]
for i in range(20):
 a=region();first=fetch(a['path']);first.save(E/f'cursor-{i+1:02}.png');move(700,600);b=invoke('repeat');second=fetch(b['path']);second.save(E/f'cursor-{i+1:02}-reference.png');box=ImageChops.difference(first,second).getbbox();cross=bool(box and box[0]>=284 and box[1]>=184)
 rows.append(dict(number=i+1,region=a,repeat=b,differenceBox=box,crossCorner=cross));(E/'cursor20.json').write_text(json.dumps(rows,indent=2));print(i+1,box,cross,flush=True)
print('corner cursor:',sum(r['crossCorner'] for r in rows),'of 20')
