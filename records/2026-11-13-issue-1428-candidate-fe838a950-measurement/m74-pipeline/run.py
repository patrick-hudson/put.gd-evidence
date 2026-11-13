from pathlib import Path
import subprocess,os,json,time
from PIL import Image,ImageDraw,ImageFont
r=Path.home()/'work/ocr-corpus-1428';w=r/'candidate-m74-pipeline';w.mkdir(mode=0o700);im=Image.new('RGB',(1920,1080),'white');d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',28)
for i,text in enumerate(['ALPHA BRAVO CHARLIE','DELTA ECHO FOXTROT','GOLF HOTEL INDIA']):d.text((35,400+45*i),text,font=font,fill='black')
p=w/'fixture.png';im.save(p);fixture=w/'show-fixture.py';fixture.write_text('import os\nos.execvp(\"feh\",[\"feh\",\"--fullscreen\",\"--zoom\",\"100\",'+repr(str(p))+'])\n');records=[]
watch=subprocess.Popen(['sudo','-n','python3',str(r/'item8-helper-watch.py'),str(w/'helper-events.jsonl')],stdout=(w/'observer.log').open('x'),stderr=subprocess.STDOUT)
for kind in ['native','appimage']:
 app=r/'ubuntu24-candidate/usr/bin/putgd' if kind=='native' else r/'putgd-26.1113.4836-dev+gfe838a950216-x86_64.AppImage';log=(w/(kind+'.log')).open('x');cmd=['python3',str(r/'item8-text-pipeline.py'),'--desktop','Mint22.3 Cinnamon6.6.4 X11 '+kind,'--leader','cinnamon','--app',str(app),'--cli',str(r/'ubuntu24-candidate/usr/bin/putgd-cli'),'--host-input',str(Path.home()/'work/i8src/tools/lab/host_input.py'),'--screen','1920','1080','--region','20','350','800','560','--expect','ALPHA BRAVO CHARLIE\nDELTA ECHO FOXTROT\nGOLF HOTEL INDIA','--needle','ALPHA BRAVO CHARLIE','--frame','--fixture','python3',str(fixture)];popen=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=os.environ|{'PYTHONPATH':str(r)});popen.wait();print('PIPELINE',kind,popen.returncode,flush=True);lines=(w/(kind+'.log')).read_text().splitlines();found=[line.removeprefix('RECEIPT ') for line in lines if line.startswith('RECEIPT ')];records.append({'kind':kind,'exit':popen.returncode,'receipt':found[-1] if found else None});(w/'index.json').write_text(json.dumps(records,indent=2))

subprocess.run(['sudo','-n','kill','-TERM',str(watch.pid)],capture_output=True);watch.wait(timeout=10)
