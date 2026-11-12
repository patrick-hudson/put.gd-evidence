import pass2 as p,fix6 as f,os,subprocess,json
P=p.P
f.control('ruler-end-2',600,['python3',str(P/'qt_fixture.py'),'--rows','600','--start','23400'],maxh=30000)
for i in range(2):
 os.environ['SC_TEXT_WIDTH']='600'
 f.with_fixture('qt600-'+str(i),['python3',str(P/'native_text_fixture.py'),'qt','600','bottom'],lambda:p.capture('qt600-'+str(i),60,30000,text=True))
f.with_fixture('gtk-repeat',['python3',str(P/'text_fixture.py'),'gtk'],lambda:p.capture('gtk-repeat',60,30000,text=True))
s=p.rpc('settings.get');p.rpc('settings.patch',{'patch':{'preferences':{'scrollCaptureFromTop':False}},'expectedRevision':s['metadata']['observedRevision']})
f.with_fixture('half-off',['python3',str(P/'qt_fixture.py'),'--rows','600','--start','12000'],lambda:p.capture('half-off',600,30000,first=12000))
s=p.rpc('settings.get');p.rpc('settings.patch',{'patch':{'preferences':{'scrollCaptureFromTop':True}},'expectedRevision':s['metadata']['observedRevision']})
f.with_fixture('stop-up',['python3',str(P/'qt_fixture.py'),'--rows','600','--start','23400'],lambda:p.capture('stop-up',600,30000,stop=.7))
for mode in ['window','narrower','shorter']:
 f.resize_case('resize-'+mode,'resize_mid_fixture.py',3,SC_MODE=mode,SC_AT='6000')
for i in range(2):
 f.with_fixture('switch'+str(i),['python3',str(P/'review_fixture.py'),'--rows','600','--start','12000','--switch'],lambda:p.capture('switch'+str(i),600,30000))
for gap in [.001,.05]:
 f.with_fixture('cancel',['python3',str(P/'qt_fixture.py'),'--rows','600'],lambda:f.cancel_case('cancel-'+str(gap),gap))
f.with_fixture('after-cancel',['python3',str(P/'qt_fixture.py')],lambda:p.capture('after-cancel',60,30000))
