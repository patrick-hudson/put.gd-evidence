from pathlib import Path
import subprocess,json,hashlib,time
r=Path.home()/'work/ocr-corpus-1428';w=r/'candidate-arch-three-languages';w.mkdir(mode=0o700);name='i81428-arch-three-final';rows={};log=(w/'setup.log').open('x');started=time.monotonic()
def call(args,**kw):return subprocess.run(['podman']+args,**kw)
try:
 p=call(['run','--name',name,'--network=host','--security-opt','label=disable','-v',str(r)+':/case:ro','-d','localhost/i81428-arch-prepared:latest','sleep','infinity'],capture_output=True,text=True,timeout=30);rows['createExit']=p.returncode;rows['containerId']=p.stdout.strip()
 if p.returncode:raise RuntimeError('create failed')
 p=call(['exec',name,'pacman','-S','--noconfirm','--needed','tesseract-data-deu','tesseract-data-fra'],stdout=log,stderr=subprocess.STDOUT,timeout=150);rows['languageInstallExit']=p.returncode
 if p.returncode:raise RuntimeError('language install failed')
 p=call(['exec',name,'python','-c',"import pathlib,json,hashlib; print(json.dumps([{ 'name':n,'bytes':(p:=pathlib.Path('/usr/share/tessdata')/(n+'.traineddata')).stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for n in ['eng','deu','fra']]))"],capture_output=True,text=True);rows['languageData']=json.loads(p.stdout);rows['dataTotal']=sum(q['bytes'] for q in rows['languageData']);rows['budgetBytes']=min(192*1024*1024,128*1024*1024+sum(q['bytes'] for q in rows['languageData'] if q['name']!='eng'))
 image=r/'synthetic-final/limit-24mp.png';helper=r/'arch-candidate/usr/bin/putgd-ocr';rows['imageSha256']=hashlib.sha256(image.read_bytes()).hexdigest();rows['helperSha256']=hashlib.sha256(helper.read_bytes()).hexdigest()
 args=['exec',name,'/case/test_ocr_run','--helper','/case/arch-candidate/usr/bin/putgd-ocr','--data','/usr/share/tessdata','--lang','eng','--lang','deu','--lang','fra','--required','/case/synthetic-final/limit-24mp.png'];rows['command']=['podman']+args
 p=call(args,capture_output=True,text=True,timeout=40);rows['driverExit']=p.returncode;rows['stderrBytes']=len(p.stderr);rows['stdoutBytes']=len(p.stdout);rows['result']=json.loads(p.stdout.strip().splitlines()[-1]);rows['status']='measured';print(rows,flush=True)
except Exception as e:rows['status']='not_run';rows['reason']=str(e);print(rows,flush=True)
finally:
 p=call(['stop','--time','3',name],stdout=log,stderr=subprocess.STDOUT,timeout=10);q=call(['rm',name],stdout=log,stderr=subprocess.STDOUT,timeout=10);rows['retired']=q.returncode==0;rows['elapsedSeconds']=time.monotonic()-started;rows['candidate']='fe838a9502167672f3512e27c32c74cfcf6c84d1';rows['scope']='Arch-only dense24MP three-language supplement; real exact-CI helper, disposable container, conservative fresh-parent child peak, not desktop latency.';(w/'receipt.json').write_text(json.dumps(rows,indent=2))
