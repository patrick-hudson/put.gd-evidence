import pass2 as p,time,subprocess,json,rfb,os
P=p.P;rpc=p.rpc;e=json.loads((P/'env.json').read_text());s=rpc('settings.get');old=s['document']['preferences']['notifications'];rpc('settings.patch',{'patch':{'preferences':{'notifications':True}},'expectedRevision':s['metadata']['observedRevision']})
f=subprocess.Popen(['python3',str(P/'qt_fixture.py'),'--rows','600'],env=e,stdout=open(P/'warning-fixture.log','w'),stderr=subprocess.STDOUT)
try:
 time.sleep(3);p.capture('cap-warning',600,2000);rfb.RFB(5901 if os.uname().nodename=='fedora' else 5900).screenshot(P/'cap-warning-visible.png');p.capture('postcap-warning',600,40000,immediate=True)
 (P/'cap-warning-history.json').write_text(json.dumps(rpc('history.list',{'limit':200}),indent=2))
finally:
 f.terminate();f.wait(10);s=rpc('settings.get');rpc('settings.patch',{'patch':{'preferences':{'notifications':old}},'expectedRevision':s['metadata']['observedRevision']})
