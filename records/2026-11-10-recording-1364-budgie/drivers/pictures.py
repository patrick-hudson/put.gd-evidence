import sys,pathlib,subprocess,json,os,time
from PIL import Image
root=pathlib.Path('/home/lab/b1364');sys.path.insert(0,str(root/'lab'));import record_run
pics=root/'pictures';pics.mkdir(exist_ok=True)
def prep(name,path,box,scale,size,at):
 im=Image.open(path).convert('RGB').crop(box)
 if scale!=1:im=im.resize((im.width*scale,im.height*scale))
 out=Image.new('RGB',size,(30,30,34));out.paste(im,at);p=pics/(name+'-input.png');out.save(p);return p
bar=prep('bar',root/'r/e/frames/pr-mp4-1-ready-on.png',(0,550,944,603),1,(1000,180),(20,90))
ring=prep('ring',root/'r/f-monitor-retained3/frames/pr-mp4-1-export-click.png',(120,40,400,180),2,(640,380),(20,80))
support=prep('support',root/'support-manual.png',(249,338,1008,577),1,(800,350),(20,75))
# Cursor comparison uses the same resting pointer position before the second press.
an=root/'an/squashfs-root'
for tag in ('f-off','f-region'):
 clip=root/'r'/tag/'out/pr-mp4-1.mp4'
 subprocess.run([str(an/'usr/bin/putgd-record'),'--preview',str(clip),'8500000',str(pics/(tag+'-cursor.png'))],env=dict(os.environ,APPDIR=str(an)),check=True,stdout=subprocess.DEVNULL)
a=Image.open(pics/'f-off-cursor.png').convert('RGB').crop((620,88,684,152));b=Image.open(pics/'f-region-cursor.png').convert('RGB').crop((620,88,684,152))
from PIL import ImageChops
counts=[sum(1 for p in im.getdata()if max(p)<70)for im in(a,b)]
(pics/'cursor-comparison.json').write_text(json.dumps({'darkPixelsPaintedDrawn':counts,'at':[640,100],'clipTimeUs':8500000}))
# Use put.gd's own editor through production session methods for all labels/arrows.
env,_=record_run.session_environment();run=root/'r/picture-editor'
for n in ('config','data','cache','state','logs'):(run/n).mkdir(parents=True,exist_ok=True)
env.update(XDG_CONFIG_HOME=str(run/'config'),XDG_DATA_HOME=str(run/'data'),XDG_CACHE_HOME=str(run/'cache'),XDG_STATE_HOME=str(run/'state'))
build=record_run.Build('pr',str(next(root.glob('*.AppImage'))),run)
def cli(method,params={}):
 v=subprocess.run([build.cli,method,json.dumps(params)],env=env,capture_output=True,text=True,timeout=65);x=json.loads(v.stdout)
 if not x.get('ok'):raise RuntimeError(str(x.get('error')))
 return x.get('result')or{}
def start():
 p=subprocess.Popen(build.launcher,env=env,stdout=open(run/'logs/resident.log','a'),stderr=subprocess.STDOUT)
 for _ in range(100):
  try:cli('settings.get');return p
  except Exception:time.sleep(.3)
 raise RuntimeError('no resident')
p=start();time.sleep(2);cli('ui.quit');p.wait(20);time.sleep(1);p=start()
log=[]
def text(s,at,size=18):return {'kind':'text','at':at,'text':s,'fontPixels':size,'color':'#ffffff'}
def arrow(a,b):return {'kind':'arrow','from':a,'to':b,'width':3,'color':'#fbbf24'}
specs=[('bar',bar,[text('Budgie 10.10.3 / labwc 0.20.2 — build 4538 / Qt 6.12.0',[18,15]),text('Microphone on; the live input meter is active',[18,48]),arrow([640,65],[523,113])]),('ring',ring,[text('Budgie — build 4538: exported clip frame',[18,15]),text('Click ring and recorder-drawn desktop cursor',[18,45],17),arrow([365,175],[188,206])]),('support',support,[text('Budgie — build 4538: Desktop support details',[18,14]),{'kind':'rectangle','rect':[28,210,735,98],'width':3,'color':'#fbbf24'}])]
try:
 for name,path,shapes in specs:
  opened=cli('editor.open',{'source':'file','path':str(path)});oid=opened.get('operationId')or opened.get('id')
  for _ in range(100):
   try:applied=cli('editor.apply',{'id':oid,'commands':[{'op':'add','shape':s}for s in shapes]});break
   except Exception:time.sleep(.2)
  saved=cli('editor.saveCopy',{'id':oid,'path':str(pics/(name+'.png'))})
  log.append({'name':name,'opened':opened,'applied':applied,'saved':saved});cli('editor.cancel',{'id':oid});time.sleep(.5)
finally:
 (pics/'editor-receipts.json').write_text(json.dumps(log,indent=2));cli('ui.quit');p.wait(20)
