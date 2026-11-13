#!/usr/bin/env python3
import json,pathlib,subprocess,sys,time,hashlib,signal,os
import record_acceptance as setup
r=setup.r

def flow(self):
 b=r.Build(*self.args.build[0].split('=',1),self.run)
 report={'rows':[]}; fixture=None; active=None; receiver=None
 def row(name,**v):
  report['rows'].append({'row':name,**v}); (self.run/'flow.json').write_text(json.dumps(report,indent=2))
 def xd(*args): return subprocess.run(['xdotool',*map(str,args)],env=self.env,capture_output=True,text=True,check=True).stdout.strip()
 def wait_editor(op):
  for _ in range(80):
   try: return self.cli(b,'editor.inspect',{'id':op})
   except r.RunError: time.sleep(.25)
  raise RuntimeError('editor never opened')
 def wait_op(op):
  for _ in range(240):
   v=self.cli(b,'operation.inspect',{'id':op})
   if v['state'] in ('completed','failed','cancelled'): return v
   time.sleep(.25)
  raise RuntimeError('operation did not finish')
 def paste(name):
  out=self.run/'paste'
  p=out/'paste.json'
  if p.exists(): p.rename(out/(name+'-previous.json'))
  wid=xd('search','--pid',fixture.pid).splitlines()[-1]
  xd('windowactivate','--sync',wid); xd('key','ctrl+v')
  for _ in range(80):
   if p.exists():
    v=json.loads(p.read_text()); (out/(name+'.json')).write_text(json.dumps(v,indent=2))
    if (out/'paste.png').exists(): (out/(name+'.png')).write_bytes((out/'paste.png').read_bytes())
    return v
   time.sleep(.1)
  raise RuntimeError('independent GTK paste did not answer')
 try:
  self.start_resident(b); time.sleep(3); self.stop_resident(b); self.open_cover(); self.start_resident(b)
  import offline_destination
  receiver,offline,origin=offline_destination.configure(self,b)
  fixture=subprocess.Popen([sys.executable,str(r.HERE/'gtk_clipboard_fixture.py'),'--output',str(self.run/'paste')],env=self.env,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=open(self.run/'logs/clipboard.log','w'))
  time.sleep(2)
  # Raise our full-screen cover before choosing a region.
  xd('windowactivate','--sync',self.cover_x11_window())
  active=self.cli(b,'editor.open',{'source':'region'})['operationId']; time.sleep(2)
  xd('mousemove',400,250); xd('mousedown',1); xd('mousemove','--sync',1050,720); xd('mouseup',1)
  state=wait_editor(active); self.desktop_frame(self.run/'frames/C-region-editor.png')
  self.cli(b,'editor.apply',{'id':active,'commands':[{'op':'add','shape':{'kind':'rectangle','rect':[30,30,150,80],'color':'#ff0000','width':4}}]})
  copied=self.cli(b,'editor.copy',{'id':active}); p=paste('C-image')
  saved=self.run/'out/editor-region.png'; self.cli(b,'editor.saveCopy',{'id':active,'path':str(saved)})
  assert p.get('image') and hashlib.sha256((self.run/'paste/C-image.png').read_bytes()).hexdigest()==copied['sha256']
  assert hashlib.sha256(saved.read_bytes()).hexdigest()==copied['sha256']
  self.cli(b,'editor.submit',{'id':active}); v=wait_op(active); assert v['items'][0]['uploadStatus']=='uploaded',v; row('C-region',passed=v['state']=='completed',operation=v); active=None
  xd('windowactivate','--sync',self.cover_x11_window())
  active=self.cli(b,'editor.open',{'source':'region'})['operationId']; time.sleep(2)
  xd('mousemove',400,250); xd('mousedown',1); xd('mousemove','--sync',1050,720); xd('mouseup',1)
  wait_editor(active); self.cli(b,'editor.cancel',{'id':active}); v=wait_op(active); active=None
  self.desktop_frame(self.run/'frames/C-cancelled.png'); row('C-cancel',passed=v['state']=='cancelled',operation=v)
  import cairo
  source=self.run/'source.png'; surface=cairo.ImageSurface(cairo.FORMAT_RGB24,900,400); c=cairo.Context(surface); c.set_source_rgb(1,1,1); c.paint(); c.set_source_rgb(0,0,0); c.select_font_face('Sans'); c.set_font_size(32); c.move_to(40,80); c.show_text('putgd acceptance synthetic text'); surface.write_to_png(str(source))
  active=self.cli(b,'editor.open',{'source':'file','path':str(source)})['operationId']; wait_editor(active)
  self.cli(b,'editor.view',{'id':active,'action':'tool','tool':'copyText'})
  for _ in range(200):
   state=self.cli(b,'editor.inspect',{'id':active})
   if state.get('text',{}).get('state') in ('completed','failed'): break
   time.sleep(.1)
  self.desktop_frame(self.run/'frames/C2-recognized.png')
  assert state['text']['state']=='completed',state.get('text')
  self.cli(b,'editor.copyText',{'id':active,'result':state['text']['result'],'all':True})
  p=paste('C2-text'); assert p.get('text','').strip()=='putgd acceptance synthetic text',p
  self.cli(b,'editor.submit',{'id':active}); v=wait_op(active); assert v['items'][0]['uploadStatus']=='uploaded',v; row('C2-file-text',passed=v['state']=='completed',operation=v,paste=p); active=None
  row('C-history',history=self.cli(b,'history.list',{'limit':20}))
 except Exception as e: row('driver-error',passed=False,error=str(e)); raise
 finally:
  if active:
   try: self.cli(b,'editor.cancel',{'id':active})
   except Exception: pass
  if fixture: fixture.terminate(); fixture.wait(10)
  self.stop_resident(b); self.close_cover()
  if receiver: receiver.shutdown(); receiver.server_close()
 return 0
r.Driver.main=flow
sys.exit(r.main())
