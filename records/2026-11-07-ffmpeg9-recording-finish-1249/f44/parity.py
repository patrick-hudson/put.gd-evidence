import json,os,subprocess,hashlib
from pathlib import Path
r=Path.home()/'work/r9b';marker=json.loads((r/'marker/results.json').read_text());o=r/'parity';o.mkdir(mode=0o700,exist_ok=True);result=[]
for row in marker['rounds']:
 if row.get('format')!='mp4' or 'clips' not in row:continue
 src=r/'marker/working'/row['clips']['working']['file']
 if not src.exists():continue
 for fmt in ['mp4','webm']:
  for b in ['candidate','nightly']:
   ad=r/'extract'/f'appdir-{b}'/'squashfs-root';h=ad/'usr/bin/putgd-record';env=dict(os.environ,APPDIR=str(ad));dst=o/f'{row["build"]}-input-{b}.{fmt}'
   z=subprocess.run([str(h),'--export',str(src),str(dst)],env=env,capture_output=True,text=True,timeout=600)
   e=dict(sourceBuild=row['build'],build=b,format=fmt,sourceSha256=hashlib.sha256(src.read_bytes()).hexdigest(),exportExit=z.returncode,exportLog=(z.stdout+z.stderr)[-1500:])
   if z.returncode==0:
    z=subprocess.run([str(h),'--av-sync',str(dst)],env=env,capture_output=True,text=True,timeout=120)
    try:e['sync']=json.loads(z.stdout)
    except:e['syncError']=z.stderr
   result.append(e);(r/'parity.json').write_text(json.dumps(result,indent=1)+'\n')
print(json.dumps(result))
