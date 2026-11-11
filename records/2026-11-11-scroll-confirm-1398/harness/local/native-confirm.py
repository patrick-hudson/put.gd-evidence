import pass2 as p,subprocess,time,json,traceback,os
P=p.P
def patch(v):
 s=p.rpc('settings.get');p.rpc('settings.patch',{'patch':v,'expectedRevision':s['metadata']['observedRevision']})
def fixture(n,cmd,call):
 e=json.loads((P/'env.json').read_text());f=subprocess.Popen(cmd,env=e,stdout=open(P/(n+'-fixture.log'),'w'),stderr=subprocess.STDOUT)
 try:time.sleep(18 if 'firefox' in cmd[0] else 3);call()
 finally:f.terminate();f.wait(15)
def ruler(n,start,rows=600,stop=None,cap=None):
 return fixture(n,['python3',str(P/'qt_fixture.py'),'--rows',str(rows),'--start',str(start)],lambda:p.capture(n,rows,cap or 40000,first=start if 'off' in n else 0,stop=stop))
try:
 p.setup();patch({'preferences':{'notifications':True,'scrollCaptureFromTop':True}})
 for i in range(3):ruler('long-bottom-%d'%i,23400)
 for kind,count in [('qt',3),('gtk',2)]:
  fixture(kind+'bottom',['python3',str(P/'text_fixture.py'),kind],lambda:[p.capture(kind+'full-bottom-%d'%i,60,60000,text=True) for i in range(count)])
 ff=P/'ffprofile';ff.mkdir();(ff/'user.js').write_text('user_pref("browser.aboutwelcome.enabled",false);user_pref("browser.shell.checkDefaultBrowser",false);user_pref("browser.startup.homepage_override.mstone","ignore");')
 html=(P/'ruler.html').read_text();(P/'bottom.html').write_text(html+'<script>setTimeout(()=>{scrollTo(0,999999);document.title="BOTTOM "+scrollY},1000)</script>')
 fixture('browserbottom',['firefox','--no-remote','--profile',str(ff),'--kiosk',(P/'bottom.html').as_uri()],lambda:[p.capture('firefox-bottom-%d'%i) for i in range(3)])
 patch({'preferences':{'scrollCaptureFromTop':False}});ruler('half-off',12000);patch({'preferences':{'scrollCaptureFromTop':True}})
 for i in range(3):ruler('plain-%d'%i,0,60)
 for i in range(2):fixture('browsertop-%d'%i,['firefox','--no-remote','--profile',str(ff),'--kiosk',(P/'ruler.html').as_uri()],lambda:p.capture('firefox-top-%d'%i))
 ruler('stop-top',23400,stop=.7)
 subprocess.run(['python3',str(P/'upload_setup.py')],check=True)
 fixture('capflow',['python3',str(P/'qt_fixture.py'),'--rows','600'],lambda:(p.capture('cap',600,2000),p.capture('postcap',600,40000,immediate=True)))
 (P/'campaign.done').write_text('done')
except Exception:
 (P/'campaign.error').write_text(traceback.format_exc());raise
