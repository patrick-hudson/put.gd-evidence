from pathlib import Path
from trial import cli,cursorpos
import sys,subprocess,json,time,hashlib
l=Path.home()/'work/s5202';label=sys.argv[1];d=l/label;c=str(l/'bin'/('cli-'+label));subprocess.run(['firefox','--profile',str(l/'ff'),'https://en.wikipedia.org/wiki/Linux'],check=True);time.sleep(5)
before_files=set((d/'out').rglob('*.png'))
s=cli(c,'scroll.prepare',{'rect':[470,200,980,720]})['result']['id'];cli(c,'scroll.start',{'id':s});time.sleep(4);before=cli(c,'scroll.inspect',{'id':s});assert before['result']['state']=='capturing',before
subprocess.run(['sudo','-n','python3',str(l/'escape.py')],check=True)
for _ in range(100):
 v=cli(c,'scroll.inspect',{'id':s})
 if v['result']['state'] in ['done','failed','cancelled']:break
 time.sleep(.1)
op={};files=[]
for _ in range(100):
 op=cli(c,'operation.inspect',{'id':s})
 if op.get('ok') and op['result'].get('state') in ['completed','failed','cancelled']:
  for item in op['result'].get('items',[]):
   local=item.get('local',{});p=Path(local.get('path','/nonexistent'))
   if local.get('status')=='saved' and p.is_file() and p not in before_files and hashlib.sha256(p.read_bytes()).hexdigest()==v['result'].get('result',{}).get('sha256'):files.append(str(p.relative_to(d)))
  break
 time.sleep(.1)
r={'beforeEscape':before,'afterEscape':v,'savedFiles':files,'saveOperation':op,'pointerAfter':cursorpos()};(d/'escape.json').write_text(json.dumps(r,indent=2));print(json.dumps(r));assert v['result']['endReason']=='stopped' and files,r
