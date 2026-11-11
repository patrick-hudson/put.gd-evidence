import pass2 as p,json,time,subprocess,re
P=p.P;rpc=p.rpc;e=json.loads((P/'env.json').read_text())
subprocess.run(['python3',str(P/'user_verify.py')],check=False)
s=rpc('settings.get');rpc('settings.patch',{'patch':{'preferences':{'scrollCaptureFromTop':True}},'expectedRevision':s['metadata']['observedRevision']})
f=subprocess.Popen(['python3',str(P/'qt_fixture.py'),'--rows','600'],env=e,stdout=open(P/'middle-fixture.log','w'),stderr=subprocess.STDOUT)
flag=[False]
def traced(m,a={}):
 v=rpc(m,a)
 if m=='scroll.inspect' and v.get('state')=='capturing' and v.get('height',0)>=12000 and not flag[0]:flag[0]=True;rpc('scroll.stop',{'id':v['id']})
 return v
try:
 time.sleep(3);p.rpc=traced;p.capture('stop-middle-final',600,40000,stop=9999)
finally:p.rpc=rpc;f.terminate();f.wait(10)
c=json.loads((P/'cancel/result.json').read_text());i=c['capture']['id'];h=rpc('history.list',{'limit':200});v={'id':i,'historyMatches':[x for x in h['records'] if x['id']==i or x.get('operationId')==i],'stagingFiles':[str(x) for x in (P/'d').rglob('*') if x.is_file() and i in str(x)]};(P/'cancel-invariants.json').write_text(json.dumps(v,indent=2))
a=json.loads((P/'stop-top2/result.json').read_text());pos=re.findall(r'position (\d+)',(P/'stop-fixture.log').read_text());a['fixtureLastPosition']=int(pos[-1]) if pos else 23400;a['currentViewportMatches']=a.get('viewportFirstPixelCandidates')==[a['fixtureLastPosition']];(P/'stop-top2/adjudication.json').write_text(json.dumps(a,indent=2))
(P/'post.done').write_text('done')
