from pathlib import Path
import subprocess,json,time,os,hashlib
class Campaign:
 def __init__(self,root):
  self.w=Path(root);self.state=json.loads((self.w/'state.json').read_text());self.env=json.loads((self.w/'private-env.json').read_text());self.desktop=json.loads((self.w/'session-env.json').read_text());self.cli=self.state['nativePrefix']+'/bin/putgd-cli';self.rows=[]
 def raw(self,method,params=None):
  p=subprocess.run([self.cli,'--socket',self.state['socket'],'--params-stdin',method],input=json.dumps(params or {}),env=self.env,capture_output=True,text=True,timeout=40);return json.loads(p.stdout)
 def call(self,method,params=None):
  v=self.raw(method,params)
  if not v.get('ok'):raise RuntimeError(v.get('error',{}).get('code','missing_reply'))
  return v['result']
 def wait(self,fn,seconds=30):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   v=fn()
   if v:return v
   time.sleep(.05)
  raise RuntimeError('observation_deadline')
 def terminal(self,op):
  return self.wait(lambda:(v if (v:=self.call('text.inspect',{'id':op}))['state'] in ['completed','failed','cancelled'] else None))
 def recognize(self,path,copy=False):return self.call('text.recognize',{'source':'file','path':str(path),'copy':copy})['operationId']
 def clip(self,text):subprocess.run(['wl-copy','--type','text/plain;charset=utf-8'],input=text.encode(),env=self.desktop,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=10)
 def paste(self,primary=False):return subprocess.run(['wl-paste','--no-newline',*(['--primary'] if primary else [])],env=self.desktop,capture_output=True,timeout=10).stdout
 def patch(self,patch):
  s=self.call('settings.get');return self.call('settings.patch',{'expectedRevision':s['metadata']['observedRevision'],'patch':patch})
 def record(self,name,measured,**metadata):
  self.rows.append(dict(case=name,status='met' if measured else 'missed',**metadata));(self.w/'group4-receipt.json').write_text(json.dumps(self.rows,indent=2))
 def open_editor(self,path):
  op=self.call('editor.open',{'source':'file','path':str(path)})['operationId']
  def ready():
   v=self.raw('editor.inspect',{'id':op})
   return v['result'] if v.get('ok') and v['result'].get('phase')=='editing' else None
  return op,self.wait(ready)
 def editor_result(self,op):
  self.call('editor.recognize',{'id':op})
  def complete():
   v=self.call('editor.inspect',{'id':op});t=v.get('text',{})
   return v if t.get('state') in ['completed','failed','cancelled'] else None
  return self.wait(complete)
