from pathlib import Path
import json,time,subprocess
from trial import cli
l=Path.home()/'work/s5302';c=str(l/'bin/cli-a');d=l/'a'
def call(m,p={}):
 v=cli(c,m,p)
 with open(d/'double-resume-calls.jsonl','a') as f:f.write(json.dumps({'method':m,'reply':v})+'\n')
 return v
subprocess.run(['firefox','--profile',str(l/'ff'),'file://'+str(l/'page.html')]);time.sleep(5)
s=call('scroll.prepare',{'rect':[470,200,980,720]})['result']['id'];call('scroll.start',{'id':s});time.sleep(2);call('scroll.pause',{'id':s});v=call('scroll.inspect',{'id':s});assert v['result']['paused'];call('scroll.resume',{'id':s});v=call('scroll.resume',{'id':s});assert not v['ok'] and v['error']['code']=='scroll_state',v
for _ in range(600):
 v=call('scroll.inspect',{'id':s})
 if v.get('result',{}).get('state') in ['done','failed','cancelled']:break
 time.sleep(.2)
(d/'double-resume.json').write_text(json.dumps(v,indent=2));assert v['result']['endReason']=='end_of_content',v
