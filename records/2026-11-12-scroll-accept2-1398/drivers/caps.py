import pass2 as p,fix6 as f,json,time,sys,rfb
P=p.P;h=sys.argv[1]
while not (P/'widths.done').exists():time.sleep(2)
if h=='f44':
 while not (P/'old-extension.done').exists():time.sleep(2)
f.with_fixture('sticky-cap',['python3',str(P/'review_fixture.py'),'--rows','600','--sticky'],lambda:p.capture('sticky-2000',600,2000,header=40,footer=40))
before=p.rpc('history.list',{'limit':200})
try:p.rpc('scroll.prepare',{'rect':[100,200,960,600],'maxHeight':20});refusal={'unexpected':'accepted'}
except Exception as ex:refusal={'error':str(ex),'limitation':'min maxHeight is 2000, larger than the 1080px desktop; footer greater than cap cannot be represented in the current selection'}
(P/'small-footer-cap-refusal.json').write_text(json.dumps(refusal,indent=2))
s=p.rpc('settings.get');p.rpc('settings.patch',{'patch':{'preferences':{'notifications':True}},'expectedRevision':s['metadata']['observedRevision']})
def visual():
 original=p.rpc
 def rpc(m,a={}):return original(m,dict(a,rect=[0,0,1900,1080]) if m=='scroll.prepare' else a)
 p.rpc=rpc;(P/'hold-upload').touch()
 try:
  p.capture('cap-visual',60,2000);(P/'reveal-warning').touch();time.sleep(1);v=rfb.RFB(5901 if h=='f44' else 5900);v.screenshot(P/'cap-warning-visible.png');v.sock.close()
 finally:
  p.rpc=original
  if (P/'hold-upload').exists():(P/'hold-upload').unlink()
f.with_fixture('cap-visual',['python3',str(P/'warning_fixture.py')],visual)
(P/'caps.done').write_text('done')
