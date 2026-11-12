from pathlib import Path
import json,os,signal,shutil,time
P=Path('/home/lab/work/s3a');procs=[];allowed={str(P/x) for x in ['qt_fixture.py','text_fixture.py','resize_mid_fixture.py','editor_fixture.py']}
for q in Path('/proc').iterdir():
 if not q.name.isdigit():continue
 try:
  cmd=[x.decode(errors='replace') for x in (q/'cmdline').read_bytes().split(bytes([0])) if x]
  if len(cmd)>1 and cmd[0].endswith('python3') and (cmd[1]=='controls7.py' or cmd[1] in allowed):procs.append({'pid':int(q.name),'args':cmd})
 except OSError:pass
print(json.dumps(procs),flush=True);(P/'cap-correction-processes.json').write_text(json.dumps(procs,indent=2))
for v in procs:
 if v['args'][1]=='controls7.py':os.kill(v['pid'],signal.SIGSTOP)
import pass2 as p
logs=[json.loads(x) for x in (P/'rpc.jsonl').read_text().splitlines()];ids=[x['reply']['result']['id'] for x in logs if x['method']=='scroll.prepare' and x['reply'].get('ok')]
if ids:
 try:
  a=p.rpc('scroll.inspect',{'id':ids[-1]});print(json.dumps(a),flush=True)
  if a['state'] not in ['done','failed','cancelled']:p.rpc('scroll.cancel',{'id':ids[-1]})
 except Exception as ex:print(str(ex),flush=True)
for v in procs:
 try:os.kill(v['pid'],signal.SIGTERM);os.kill(v['pid'],signal.SIGCONT)
 except ProcessLookupError:pass
time.sleep(1);out=P/'cap-correction-attempt';out.mkdir()
for n in ['ruler-end-0','ruler-end-1','qtfull-00','gtkfull-00','mid-viewport-0','editor-0','controls7.json','controls7.done']:
 if (P/n).exists():(P/n).rename(out/n)
for n in ['helper.log','rpc.jsonl','pass2.py','fix6.py','controls7.py']:shutil.copyfile(P/n,out/n)
for n in ['pass2.py','fix6.py','controls7.py','startcancel.py']:
 f=P/n;f.write_text(f.read_text().replace('40000','30000').replace('60000','30000'))
(P/'cap-correction.json').write_text(json.dumps({'reason':'d69 cap ceiling30000 applies to guest lane too','observedState':a if ids else None,'originalAttemptsPreserved':str(out),'correctedCommand':'python3 controls7.py ruler text resize minimap'},indent=2))
print('corrected cap defaults; original attempt retained',flush=True)
