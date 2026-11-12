import pass2 as p,fix6 as f,subprocess,time,json
P=p.P
subprocess.run(['python3',str(P/'upload_setup.py')],check=True)
s=p.rpc('settings.get');p.rpc('settings.patch',{'patch':{'preferences':{'notifications':True}},'expectedRevision':s['metadata']['observedRevision']})
f.with_fixture('capflow',['python3',str(P/'qt_fixture.py'),'--rows','600'],lambda:(p.capture('cap',600,2000),p.capture('postcap',600,30000,immediate=True)))
