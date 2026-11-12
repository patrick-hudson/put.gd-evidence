import socket,json,time,subprocess,os,sys,base64,hashlib,shutil,traceback
from pathlib import Path
P=Path('/home/patrick/work/sl25');sys.path.insert(0,str(P));import pass2 as p,record_run,rfb
class Marionette:
 def __init__(self):
  self.s=socket.create_connection(('127.0.0.1',28281),5);self.s.settimeout(90);self.i=0;self.recv();self.cmd('WebDriver:NewSession',{})
 def recv(self):
  b=b''
  while not b.endswith(b':'):b+=self.s.recv(1)
  n=int(b[:-1]);b=b''
  while len(b)<n:b+=self.s.recv(n-len(b))
  return json.loads(b)
 def cmd(self,m,a={}):
  self.i+=1;b=json.dumps([0,self.i,m,a]).encode();self.s.sendall(str(len(b)).encode()+b':'+b);r=self.recv()
  if r[2]:raise RuntimeError(r[2])
  return r[3]
 def js(self,s):
  v=self.cmd('WebDriver:ExecuteScript',{'script':s,'args':[],'newSandbox':True,'sandbox':'default','line':0,'filename':'live25-read-only'})
  return v.get('value',v) if isinstance(v,dict) else v
 def wheel(self,dy):
  self.cmd('WebDriver:PerformActions',{'actions':[{'type':'wheel','id':'wheel','actions':[{'type':'scroll','x':600,'y':450,'deltaX':0,'deltaY':int(dy),'duration':200,'origin':'viewport'}]}]});time.sleep(.6)
 def shot(self,f):
  r=self.cmd('WebDriver:TakeScreenshot',{'id':None,'highlights':[],'full':True});s=r.get('value',r) if isinstance(r,dict) else r;f.write_bytes(base64.b64decode(s))
 def info(self):return self.js('''return {url:location.href,title:document.title,user:document.querySelector('meta[name="user-login"]')?.content||'',signedOut:!!document.querySelector('a[href^="/login"]'),x:mozInnerScreenX,y:mozInnerScreenY,w:innerWidth,h:innerHeight,dpr:devicePixelRatio,clientWidth:document.documentElement.clientWidth,scrollY,docHeight:document.documentElement.scrollHeight,loadingImages:[...document.images].filter(i=>!i.complete).length,anchors:[...document.querySelectorAll('[id]')].filter(e=>/^(issuecomment-\d+|discussion_r\d+|pullrequestreview-\d+)$/.test(e.id)&&e.getBoundingClientRect().height>0).map(e=>({id:e.id,y:e.getBoundingClientRect().top+scrollY,time:e.querySelector('relative-time')?.getAttribute('datetime')})),loadMore:[...document.querySelectorAll('button')].filter(e=>/load more/i.test(e.textContent)).map(e=>({text:e.textContent.trim().slice(0,100),y:e.getBoundingClientRect().top+scrollY}))};''')
if __name__=='__main__' and sys.argv[1]=='start':
 p.setup();e=json.loads((P/'env.json').read_text())
 # Only the isolated test dashboard is closed.
 for q in Path('/proc').iterdir():
  if not q.name.isdigit():continue
  try:
   if (q/'comm').read_text().strip()=='putgd-ui' and ('XDG_CONFIG_HOME='+str(P/'c')).encode() in (q/'environ').read_bytes().split(bytes([0])):os.kill(int(q.name),15)
  except OSError:pass
 prof=P/'firefox';prof.mkdir(mode=0o700);(prof/'user.js').write_text('user_pref("marionette.port",28281);user_pref("browser.aboutwelcome.enabled",false);user_pref("browser.shell.checkDefaultBrowser",false);user_pref("browser.startup.homepage_override.mstone","ignore");user_pref("browser.sessionstore.resume_from_crash",false);')
 ff=subprocess.Popen(['firefox','--new-instance','--no-remote','--marionette','--profile',str(prof),'about:blank'],env=dict(e,MOZ_DBUS_REMOTE='0',MOZ_NO_REMOTE='1'),stdout=open(P/'firefox.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(P/'firefox.pid').write_text(str(ff.pid));time.sleep(8)
 m=Marionette();print(m.cmd('WebDriver:MaximizeWindow'));m.cmd('WebDriver:Navigate',{'url':'https://github.com/patrick-hudson/put.gd-desktop/pull/1398'});time.sleep(12);info=m.info();(P/'initial-dom.json').write_text(json.dumps(info,indent=2));print(json.dumps(info));m.shot(P/'reference-initial.png');print('READY')
