import pass2 as p,fix6 as f,sys,time,rfb,json,subprocess
P=p.P;h=sys.argv[1];s=p.rpc('settings.get');p.rpc('settings.patch',{'patch':{'preferences':{'notifications':True,'scrollCaptureFromTop':True}},'expectedRevision':s['metadata']['observedRevision']})
original=p.rpc
(P/'hold-upload').touch()
def fullrpc(m,a={}):return original(m,dict(a,rect=[0,0,1900,1080]) if m=='scroll.prepare' else a)
def run():
 p.rpc=fullrpc
 try:p.capture('cap-warning',600,2000)
 finally:p.rpc=original
 (P/'reveal-warning').touch();time.sleep(1);v=rfb.RFB(5989);v.screenshot(P/'cap-warning-visible.png');v.sock.close()
try:f.with_fixture('warning',['python3',str(P/'warning_fixture.py'),'--rows','600'],run)
finally:
 p.rpc=original
 if (P/'hold-upload').exists():(P/'hold-upload').unlink()
subprocess.run(['python3',str(P/'payload-proof.py')],check=True)
