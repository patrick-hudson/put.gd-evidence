import pass2 as p,fix6 as f,subprocess,time,json,sys,traceback
P=p.P;h=sys.argv[1]
while not (P/'campaign.done').exists() and not (P/'campaign.error').exists():time.sleep(2)
def attempt(n,fn):
 try:fn()
 except Exception:(P/(n+'.error')).write_text(traceback.format_exc())
if h=='f44':
 for i in range(3):attempt('retest'+str(i),lambda i=i:f.control('valid-long-bottom-'+str(i),600,['python3',str(P/'qt_fixture.py'),'--rows','600','--start','23400'],maxh=40000))
for mode in ['window','viewport','narrower','shorter']:attempt('mid-'+mode,lambda mode=mode:f.resize_case('mid-'+mode,'resize_mid_fixture.py',3,SC_MODE=mode,SC_AT='6000'))
attempt('timer',lambda:f.resize_case('timer-resize','resize_window_fixture.py',1))
for i in range(2):attempt('switch'+str(i),lambda i=i:f.with_fixture('switch-'+str(i),['python3',str(P/'review_fixture.py'),'--rows','600','--start','12000','--switch'],lambda:p.capture('switch-'+str(i),600,40000)))
for gap,num in [(.001,5 if h in ['f44','d69'] else 1),(.05,3 if h in ['f44','d69'] else 1)]:
 for i in range(num):attempt('cancel'+str(gap)+str(i),lambda gap=gap,i=i:f.with_fixture('cancel', ['python3',str(P/'qt_fixture.py'),'--rows','600'],lambda:f.cancel_case('cancel-'+str(gap)+'-'+str(i),gap)))
attempt('after-cancels',lambda:f.with_fixture('after-cancels',['python3',str(P/'qt_fixture.py')],lambda:p.capture('after-cancels',60,40000)))
(P/'extra.done').write_text('done')
