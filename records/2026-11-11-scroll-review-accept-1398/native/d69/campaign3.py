import pass2 as p,sys,json,time,subprocess,re
P=p.P
host=sys.argv[1]
for kind,n in [('firefox',5),('qtfull',3),('gtkfull',3),('qtnarrowfull',3),('gtknarrowfull',3)]:
 p.batch(kind,n)
if host=='d69':p.batch('long',1)
for j in range(3 if host=='d69' else 1):
 e=json.loads((P/'env.json').read_text()); log=P/('stoptop-%d-fixture.log'%j)
 f=subprocess.Popen(['python3',str(P/'qt_fixture.py'),'--rows','600','--start','23400'],env=e,stdout=open(log,'w'),stderr=subprocess.STDOUT)
 try:
  time.sleep(3);r=p.capture('stoptop-%d'%j,600,40000,stop=.9)
  positions=re.findall(r'position (\d+)',log.read_text());last=int(positions[-1]) if positions else 23400
  r['visibleFixtureLastPosition']=last;r['currentViewportCorrect']=r.get('viewportFirstPixelCandidates')==[last]
  (P/('stoptop-%d'%j)/'adjudication.json').write_text(json.dumps(r,indent=2))
 finally:f.terminate();f.wait(10)
if host=='f44':p.batch('race',5)
(P/'campaign-complete').write_text('done')
