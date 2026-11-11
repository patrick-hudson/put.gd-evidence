import pass2 as p,json,time,subprocess,sys
P=p.P;rpc=p.rpc;e=json.loads((P/'env.json').read_text())
def patch(patch):
 s=rpc('settings.get');return rpc('settings.patch',{'patch':patch,'expectedRevision':s['metadata']['observedRevision']})
def fixture(name,args,fn):
 f=subprocess.Popen(['python3',str(P/'qt_fixture.py')]+args,env=e,stdout=open(P/(name+'-fixture.log'),'w'),stderr=subprocess.STDOUT)
 try:time.sleep(3);return fn()
 finally:f.terminate();f.wait(10)
if sys.argv[1]=='mint':
 fixture('sticky',['--sticky'],lambda:p.capture('sticky',header=40,footer=40))
 fixture('half-on',['--start','1200'],lambda:p.capture('half-on'))
 patch({'preferences':{'scrollCaptureFromTop':False}})
 try:
  fixture('half-off',['--start','1200'],lambda:p.capture('half-off',first=1200))
  fixture('stop-half',['--rows','1000'],lambda:p.capture('stop-half',1000,60000,stop=2))
  def cancel():
   out=P/'cancel';out.mkdir();before=rpc('history.list',{'limit':200});offset=(P/'helper.log').stat().st_size
   v=rpc('scroll.prepare',{'rect':[100,200,960,600]});i=v['id'];time.sleep(1);rpc('scroll.start',{'id':i});time.sleep(1);rpc('scroll.cancel',{'id':i});v=rpc('scroll.inspect',{'id':i});after=rpc('history.list',{'limit':200})
   import rfb;rfb.RFB(5900).screenshot(out/'screen.png')
   (out/'helper.log').write_bytes((P/'helper.log').read_bytes()[offset:]);(out/'result.json').write_text(json.dumps({'capture':v,'pass':v['state']=='cancelled' and before==after,'before':before,'after':after},indent=2))
  fixture('cancel',['--rows','1000'],cancel)
 finally:patch({'preferences':{'scrollCaptureFromTop':True}})
elif sys.argv[1]=='cap':
 subprocess.run(['python3',str(P/'upload_setup.py')],check=True)
 p.batch('cap',1)
 import rfb;rfb.RFB(5901 if sys.argv[2]=='f44' else 5900).screenshot(P/'cap-notification.png')
 (P/'cap-history.json').write_text(json.dumps(rpc('history.list',{'limit':200}),indent=2))
elif sys.argv[1]=='mcpfixture':
 f=subprocess.Popen(['python3',str(P/'qt_fixture.py'),'--rows','600','--start','23400'],env=e,stdout=open(P/'mcp-fixture.log','w'),stderr=subprocess.STDOUT);(P/'mcp-fixture.pid').write_text(str(f.pid))
