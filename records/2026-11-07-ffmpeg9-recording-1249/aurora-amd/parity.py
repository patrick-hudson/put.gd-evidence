import json,os,subprocess,hashlib,sys
from pathlib import Path
root=Path.home()/'work/f9t';marker=json.loads((root/'marker/results.json').read_text());out=root/'parity';out.mkdir(mode=0o700);result=[]
for row in marker['rounds']:
 if row['format'] not in ['mp4','webm'] or 'clips' not in row:continue
 src=root/'marker/working'/row['clips']['working']['file']
 if not src.exists():continue
 fmt=row['format']
 for b in ['candidate','nightly']:
  ad=root/sys.argv[1]/f'appdir-{b}/squashfs-root';helper=ad/'usr/bin/putgd-record';env=dict(os.environ,APPDIR=str(ad))
  dst=out/f'{row["build"]}-input-{b}.{fmt}'
  r=subprocess.run([str(helper),'--export',str(src),str(dst)],env=env,capture_output=True,text=True,timeout=600)
  entry={'sourceBuild':row['build'],'build':b,'format':fmt,'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'exportExit':r.returncode,'exportLog':(r.stdout+r.stderr)[-1500:]}
  if r.returncode==0:
   s=subprocess.run([str(helper),'--av-sync',str(dst)],env=env,capture_output=True,text=True,timeout=120)
   try:entry['sync']=json.loads(s.stdout)
   except:entry['syncError']=s.stderr
  result.append(entry);(root/'parity.json').write_text(json.dumps(result,indent=1)+'\n')
print(json.dumps(result))
