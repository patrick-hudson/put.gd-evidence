import pass2 as p,subprocess,json,time,os,shutil,hashlib,rfb,traceback,sys
P=p.P;e=json.loads((P/'env.json').read_text());d=P/'user';d.mkdir();off=(P/'helper.log').stat().st_size
s=p.rpc('settings.get');patch={'actions':{k:{'shortcut':'Ctrl+Shift+F8' if k=='scroll' else ''} for k in s['document']['actions']}}
p.rpc('settings.patch',{'patch':patch,'expectedRevision':s['metadata']['observedRevision']})
f=subprocess.Popen(['python3',str(P/'qt_fixture.py')],env=e,stdout=open(d/'fixture.log','w'),stderr=subprocess.STDOUT)
try:
 time.sleep(3);before=p.rpc('history.list',{'limit':200});v=rfb.RFB(5901 if sys.argv[1]=='f44' else 5900);v.frame();v.screenshot(d/'before.png');v.key('ctrl','shift','f8');time.sleep(1);v.screenshot(d/'selector.png');v.drag(100,200,1060,800);time.sleep(1);v.screenshot(d/'after-drag.png');v.sock.close()
 old={r['id'] for r in before['records']};new=[]
 for i in range(200):
  after=p.rpc('history.list',{'limit':200});new=[r for r in after['records'] if r['id'] not in old]
  if new and new[0]['local'].get('path'):break
  time.sleep(.2)
 (d/'history.json').write_text(json.dumps({'before':before,'after':after,'new':new},indent=2))
 if len(new)==1 and new[0]['local'].get('path'):
  shutil.copyfile(new[0]['local']['path'],d/'capture.png')
  import scroll_run,argparse
  a=argparse.Namespace(scale=1,height=2400,rows=60,first_pixel=0,header=0,footer=0,code_width=960,format='fixture',scrollbar=0)
  (d/'verification.json').write_text(json.dumps(scroll_run.verify(d/'capture.png',a),indent=2))
finally:
 f.terminate();f.wait(10);(d/'helper.log').write_bytes((P/'helper.log').read_bytes()[off:])
