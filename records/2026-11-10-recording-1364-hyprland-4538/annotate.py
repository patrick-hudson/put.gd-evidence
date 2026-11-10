import os,json,time,pathlib,subprocess,sys
from PIL import Image
sys.path.insert(0,str(pathlib.Path.home()/'lab'));import record_run
H=pathlib.Path.home();out=H/'pictures';out.mkdir(exist_ok=True);env,_=record_run.session_environment()
for k,v in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_STATE_HOME','state'),('XDG_CACHE_HOME','cache')]:
 p=H/'annotation'/v;p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
p=subprocess.Popen(['/usr/bin/putgd','--background'],env=env,stdout=open(H/'annotation.log','w'),stderr=subprocess.STDOUT)
def cli(m,a={}):
 r=subprocess.run(['/usr/bin/putgd-cli',m,json.dumps(a)],env=env,capture_output=True,text=True);x=json.loads(r.stdout);assert x['ok'],x;return x.get('result',{})
for i in range(60):
 try:cli('capabilities');break
 except Exception:time.sleep(.5)
try:
 for name,src,crop,shapes in [
 ('microphone-on',H/'bar/shots/on.png',(336,670,1280,724),[{'kind':'rectangle','rect':[370,6,175,42]}]),
 ('no-microphone',H/'bar/shots/none.png',(336,670,1280,724),[{'kind':'rectangle','rect':[395,6,170,42]}]),
 ('click-ring',H/'r/g-region/frames/pr-mp4-1-export-click.png',None,[{'kind':'arrow','from':[340,70],'to':[223,93]},{'kind':'text','at':[340,35],'text':'Click ring - PR 4538','fontPixels':22}])]:
  pic=Image.open(src)
  if crop:pic=pic.crop(crop)
  raw=out/(name+'-raw.png');pic.save(raw)
  op=cli('editor.open',{'source':'file','path':str(raw)})['operationId']
  for i in range(60):
   try:
    if cli('editor.inspect',{'id':op}).get('phase')=='editing':break
   except AssertionError as error:
    if 'editor_starting' not in str(error):raise
   time.sleep(.25)
  for shape in shapes:shape.setdefault('color','#ff2d55');shape.setdefault('width',3)
  cli('editor.apply',{'id':op,'commands':[{'op':'add','shape':s} for s in shapes]})
  cli('editor.saveCopy',{'id':op,'path':str(out/(name+'.png')),'overwrite':True});cli('editor.cancel',{'id':op});print(name,flush=True)
finally:
 cli('ui.quit');p.wait(10)
