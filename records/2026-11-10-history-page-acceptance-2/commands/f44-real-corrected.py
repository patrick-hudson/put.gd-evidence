from session_base import *
import pyatspi,rfb
from PIL import Image
root=Path('/tmp/hp2s');root.mkdir(mode=0o700)
native,desktop=session_environment();native.update(QT_QPA_PLATFORM='xcb')
for l in subprocess.check_output(['systemctl','--user','show-environment'],text=True).splitlines():
 k,_,v=l.partition('=')
 if k in ('DISPLAY','XAUTHORITY'):native[k]=v
keeper=subprocess.Popen(['python3',str(Path.home()/'putgd-lab/h1396-ci/p2-clipboard.py'),str(root)],env=native,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
print(keeper.stdout.readline(),flush=True)
ready=json.loads(keeper.stdout.readline());print(json.dumps(ready),flush=True)
assert ready.get('ready')
env,desktop=session_environment();env.update(QT_LINUX_ACCESSIBILITY_ALWAYS_ON='1',QT_ACCESSIBILITY='1');env['PIPEWIRE_RUNTIME_DIR']=env['XDG_RUNTIME_DIR']
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_STATE_HOME','state'),('XDG_CACHE_HOME','cache'),('XDG_RUNTIME_DIR','runtime')]:
 (root/sub).mkdir(mode=0o700);env[key]=str(root/sub)
(root/'files').mkdir(mode=0o700);(root/'config/putgd').mkdir(mode=0o700);DOC['archive']['root']=str(root/'files');(root/'config/putgd/config.json').write_text(json.dumps(DOC))
sock=str(root/'runtime/putgd/session.sock');assert len(sock.encode())<=107;print('socket',sock,len(sock.encode()),flush=True)
app=Path.home()/'putgd-lab/h1396-ci/p2-app/squashfs-root'
ce=env.copy();ce.update(LD_LIBRARY_PATH=str(app/'usr/lib')+':'+str(app/'usr/lib/putgd'),QT_PLUGIN_PATH=str(app/'usr/plugins')+':'+str(app/'usr/lib/qt6/plugins'))
log=[];results={};resident=None
os.environ.update(native)
def call(m,p={}):
 q=subprocess.run([str(app/'usr/bin/putgd-cli'),m,json.dumps(p)],env=ce,capture_output=True,text=True,timeout=40)
 v=json.loads(q.stdout);log.append({'method':m,'params':p,'reply':v});(root/'commands.json').write_text(json.dumps(log,indent=2));return v

def start():
 global resident
 with (root/'app.log').open('a') as f:resident=subprocess.Popen([str(app/'AppRun'),'--background'],env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=f,start_new_session=True)
 for _ in range(100):
  if Path(sock).exists():return
  time.sleep(.1)
 raise RuntimeError('socket unavailable')
def state():
 for _ in range(50):
  s=call('ui.history',{'action':'inspect'})['result']
  if not s.get('busy') and not s.get('page',{}).get('loading'):return s
  time.sleep(.15)
 raise RuntimeError('history busy')
def action(a,**kw):
 r=call('ui.history',dict(action=a,**kw));state();return r

def own():
 rows=[]
 for a in pyatspi.Registry.getDesktop(0):
  try:
   pid=a.get_process_id()
   if 'putgd' not in Path('/proc/'+str(pid)+'/exe').resolve().name:continue
   for w in a:
    if w.name=='put.gd' and w.getState().contains(pyatspi.STATE_SHOWING):rows.append((w,pid))
  except (OSError,RuntimeError):pass
 assert len(rows)==1,'one visible owned put.gd frame required'
 w,pid=rows[0];e=w.queryComponent().getExtents(pyatspi.DESKTOP_COORDS);return w,pid,(e.x,e.y,e.width,e.height)
def focus():
 w,pid,b=own();assert w.getState().contains(pyatspi.STATE_ACTIVE),'owned frame focus required'
 r=rfb.RFB(5901)
 try:
  sw,sh=r.width,r.height
  if b[2]!=sw:
   r.key('alt','f10');time.sleep(.5);w,pid,b=own()
  assert b[2]==sw and b[3]==sh-32, ('not a verified maximized GNOME client',b,sw,sh)
 finally:r.close()
 return (0,32,b[2],b[3])
def shot(n):
 b=focus();r=rfb.RFB(5901)
 try:sw,sh,pix=r.frame()
 finally:r.close()
 x,y,w,h=b;assert x>=0 and y>=0 and x+w<=sw and y+h<=sh
 Image.frombytes('RGB',(sw,sh),pix,'raw','BGRX').crop((x,y,x+w,y+h)).save(root/(n+'.png'))
 print('saved owned active AT-SPI frame',n,b,flush=True)
def key(*names):
 focus();r=rfb.RFB(5901)
 try:r.key(*names)
 finally:r.close()
 time.sleep(.2)
def click(x,y,double=False):
 a,b,w,h=focus();assert 0<x<w and 0<y<h;r=rfb.RFB(5901)
 try:
  r.click(a+x,b+y)
  if double:time.sleep(.08);r.click(a+x,b+y)
 finally:r.close()
 time.sleep(.2)
try:
 start();print(json.dumps(call('diagnostics')),flush=True);call('capabilities');call('settings.get')
 # A submitted file is synthetic and local only; clipboard lease is already ready.
 import struct,zlib
 def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
 (root/'synthetic.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',64,64,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\x00'+b'\x33\x88\xbb'*64)*64))+chunk(b'IEND',b''))
 oid=call('editor.open',{'source':'file','path':str(root/'synthetic.png')})['result']['operationId'];time.sleep(.5);call('editor.submit',{'id':oid})
 for _ in range(100):
  if call('operation.inspect',{'id':oid})['result']['state']=='completed':break
  time.sleep(.1)
 call('ui.quit');resident.wait(timeout=15)
 import native_acceptance as n
 print(json.dumps(n.grow_database(root/'data/putgd/history.sqlite',236)),flush=True)
 with sqlite3.connect(root/'data/putgd/history.sqlite') as c:
  from datetime import datetime,timedelta,timezone
  c.row_factory=sqlite3.Row
  for i,row in enumerate(list(c.execute('select * from history order by created desc'))):
   d=json.loads(row['data']);created=(datetime(2026,11,10,18,tzinfo=timezone.utc)-timedelta(days=i//80,seconds=i%80)).isoformat(timespec='milliseconds').replace('+00:00','Z');d.update(created=created,name='Synthetic-history-%03d.png'%i)
   if i%17==0:d.update(uploadStatus='failed',error={'code':'synthetic_failure','message':'Synthetic upload failure','details':{}})
   c.execute('update history set created=?,name=?,upload_status=?,data=? where id=?',(created,d['name'],d['uploadStatus'],json.dumps(d).encode(),row['id']))
 start();call('ui.show',{'view':'history'});time.sleep(1);shot('00-initial')
 counts=call('history.counts')['result']
 for cat in ('all','images','videos','text+other','failed'):
  action('showCategory',category=cat);assert state()['categoryTotals']==counts['categories'];shot('01-'+cat)
 assert action('removeFilter',key='uploadStatus')['error']['code']=='history_filter_locked';results['1']='pass'
 action('showCategory',category='all');action('setFilter',key='mime',value='image/png');action('setFilter',key='localStatus',value='saved');assert len(state()['filterChips'])==2;shot('02-filters');action('removeFilter',key='mime');action('clearFilters',scope='all');results['2']='partial: filters pass; real search pending'
 action('goToPage',page=2);shot('03-page2');action('goToPage',page=5);assert state()['page']['lastItem']==236;assert action('nextPage')['error']['code']=='history_page_unavailable';shot('03-last');results['3']='partial: API paging pass; real Alt keys pending'
 action('goToPage',page=2);shot('04-continued');results['4']='partial: day continuation captured; pin scrolling pending'
 ids=[r['id'] for r in call('history.list')['result']['records']];action('goToPage',page=1);action('select',ids=[ids[1]]);action('closeDetails');action('select',ids=[ids[2]]);assert not state()['inspectorVisible'];action('openDetails');assert state()['inspectorVisible'];action('toggleDetails');assert not state()['detailsWanted'];shot('05-closed');results['5']='partial: API details actions pass; real close/Enter/Esc/double click pending'
 results['6']='not run: heading real input pending'
 action('select',ids=ids[1:4]);assert state()['selectionHeader'];shot('07-selection');results['7']='not run: local-only fixture has no share links or deletable remote objects'
 action('setView',view='gallery');shot('08-gallery');action('setView',view='list');shot('08-list');results['8']='partial: view switch pass; real gallery keys pending'
 for theme in ('light','dark'):
  cur=call('settings.get')['result'];call('settings.patch',{'expectedRevision':cur['metadata']['observedRevision'],'patch':{'preferences':{'appearance':{'theme':theme}}}});time.sleep(.3);shot('09-'+theme)
 results['9']='partial: themes pass; minimum-size pending'

 def test(label,fn):
  try:fn();results[label]='pass'
  except Exception as e:results[label]='fail: '+repr(e)
  shot(label+'-real')
 def search():
  action('clearSelection');action('setView',view='list');action('clearFilters',scope='all');click(1350,140);key('ctrl','a');key('0');key('0');key('1');key('ret');assert state()['query']['search']=='001';assert state()['page']['total']==1;action('clearFilters',scope='all')
 test('2',search)
 def pagingkeys():
  action('clearSelection');action('setView',view='list');action('clearFilters',scope='all');action('goToPage',page=1);click(500,310);action('openDetails');key('esc')
  def listfocused():
   def walk(n):
    if n.name=='History items and upload activity' and n.getState().contains(pyatspi.STATE_FOCUSED):return True
    return any(walk(c) for c in n)
   return walk(own()[0])
  for _ in range(30):
   if listfocused():break
   key('tab')
  assert listfocused(),'native list keyboard focus unavailable'
  key('alt','right');assert state()['page']['page']==2;key('alt','left');assert state()['page']['page']==1
 test('3',pagingkeys)
 def days():
  action('goToPage',page=2);assert any('continued' in d.get('heading','') for d in state()['days']);action('goToPage',page=1)
  x,y,w,h=focus();r=rfb.RFB(5901)
  try:r.scroll(1100,650,-3)
  finally:r.close()
  shot('04-scroll')
 test('4',days)
 def details():
  action('goToPage',page=1);action('select',ids=[ids[1]]);action('openDetails');click(1876,200);assert not state()['detailsWanted'];action('select',ids=[ids[2]]);assert not state()['inspectorVisible'];click(500,380);key('ret');assert state()['inspectorVisible'];key('esc');assert not state()['detailsWanted'];click(500,380,double=True);assert state()['inspectorVisible'];key('esc');call('ui.close',{'view':'history'});call('ui.show',{'view':'history'});assert not state()['detailsWanted']
 test('5',details)
 def heading():
  action('closeDetails');action('goToPage',page=1);action('select',ids=[ids[1]]);before=state()['selectedIds'];click(400,180);assert state()['selectedIds']==before
 test('6',heading)
 def gallery():
  action('setView',view='gallery');action('clearSelection');click(350,390);key('esc');key('shift','right');assert state()['selectedRows']==2;before=state()['selectedIds'];key('down');assert state()['selectedRows']==1 and state()['selectedIds']!=before
 test('8',gallery)
 results['10']='pending visual review'

except Exception as e:
 results['stopped']=repr(e);print('ERROR',repr(e),flush=True)
finally:
 try:
  if Path(sock).exists():call('ui.quit')
  if resident:resident.wait(timeout=15)
 except Exception as e:results['quit_error']=repr(e)
 keeper.stdin.close();keeper.wait(timeout=10);results['clipboard_restored']=keeper.returncode==0
 (root/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results),flush=True)
