import pass2 as p,fix6 as f,json
s=p.rpc('settings.get');p.rpc('settings.patch',{'patch':{'preferences':{'scrollCaptureFromTop':True,'notifications':False}},'expectedRevision':s['metadata']['observedRevision']})
for i in range(2):
 name='gtk-capfit-'+str(i)
 f.with_fixture(name,['python3',str(p.P/'gtk-capfit-fixture.py'),'gtk'],lambda:p.capture(name,60,30000,text=True))
