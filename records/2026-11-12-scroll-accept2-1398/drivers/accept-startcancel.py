import pass2 as p,fix6 as f,time,sys,json,traceback,rfb
P=p.P;h=sys.argv[1]
while not (P/'presentation.done').exists():time.sleep(2)
def run(i):
 d=P/('cancel-start-'+str(i));d.mkdir();off=(P/'helper.log').stat().st_size
 v=p.rpc('scroll.prepare',{'rect':[100,200,960,600]});ident=v['id']
 while v['state']!='ready':time.sleep(.05);v=p.rpc('scroll.inspect',{'id':ident})
 p.rpc('scroll.start',{'id':ident});reply=p.rpc('scroll.cancel',{'id':ident});v=p.rpc('scroll.inspect',{'id':ident});time.sleep(2)
 rfb.RFB(5901 if h=='f44' else 5900).screenshot(d/'screen-2s-later.png')
 (d/'result.json').write_text(json.dumps({'capture':v,'reply':reply,'pass':v['state']=='cancelled'},indent=2));(d/'helper.log').write_bytes((P/'helper.log').read_bytes()[off:])
for i in range(3 if h in ['f44','d69'] else 1):
 try:f.with_fixture('cancel-start',['python3',str(P/'qt_fixture.py'),'--rows','600'],lambda i=i:run(i))
 except Exception:(P/('cancel-start-'+str(i)+'.error')).write_text(traceback.format_exc())
f.with_fixture('final-next',['python3',str(P/'qt_fixture.py')],lambda:p.capture('final-next',60,40000))
(P/'controls.done').write_text('done')
