from pathlib import Path
import subprocess,os,json,re,signal,resource
r=Path.home()/'work/ocr-final-1428';w=r/'candidate-confinement';w.mkdir(mode=0o700);probe=Path.home()/'work/final1428src/build/release/test_ocr_confinement_probe';outside=w/'read-control.txt';outside.write_text('synthetic outside-read control\n');target=w/'must-not-be-written.txt';rows=[];env=os.environ|{'PUTGD_TEXT_DATA':'/usr/share/tesseract-ocr/5/tessdata'}
for phase in ['--recognize','--bands']:
 for action,arg in [('none',None),('socket-inet',None),('socket-unix',None),('exec',None),('fork',None),('write',str(target)),('read',str(outside)),('vm-read',str(os.getpid()))]:
  cmd=[str(probe),phase,action]+([arg] if arg else []);p=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=35);abi=re.search(r'abi=(\d+)',p.stdout);recognized=re.search(r'recognized error= bands=(\d+)',p.stdout);denied=p.returncode==-signal.SIGSYS or bool(re.search(r'result=-1 errno=(1|13)\b',p.stdout));row={'phase':phase,'action':action,'exit':p.returncode,'stdout':p.stdout,'stderrBytes':len(p.stderr),'abi':int(abi.group(1)) if abi else None,'bands':int(recognized.group(1)) if recognized else None,'status':'not_run'}
  if abi and recognized and (phase!='--bands' or int(recognized.group(1))>1):row['status']='met' if (p.returncode==0 if action=='none' else denied) else 'missed'
  if action=='write' and target.exists():row['status']='missed'
  rows.append(row);(w/'receipt.json').write_text(json.dumps({'candidate':'357210d2f1cb7b65f77166e34eb535d42e497fd0','scope':'provided test build using helper confinement/engine; native distro OpenMP','rows':rows},indent=2));print(phase,action,row['status'],flush=True)
