import sys,struct,os,array,socket,time,json
sys.path.insert(0,'/tmp');import wayland_toplevels as w
class Probe(w.Client):
 def dispatch(self,obj,op,r):
  if self.objects.get(obj)=='layer' and op==0:self.serial=r.uint();self.configured=True
  elif self.objects.get(obj)=='layer' and op==1:self.closed=True
  else:super().dispatch(obj,op,r)
p=Probe(w.socket_path(None));p.configured=False;p.closed=False
p.registry=p.new_id('wl_registry');p.send(w.message(1,1,struct.pack('<I',p.registry)));p.sync()
def bind(name,version,kind):p.bind(name,version,kind);return p.next_id-1
comp=bind('wl_compositor',4,'compositor');shm=bind('wl_shm',1,'shm');layers=bind('zwlr_layer_shell_v1',1,'layers')
surf=p.new_id('surface');p.send(w.message(comp,0,struct.pack('<I',surf)))
layer=p.new_id('layer');p.send(w.message(layers,0,struct.pack('<IIII',layer,surf,0,3)+w.encode_string('privacy-probe')))
p.send(w.message(layer,0,struct.pack('<II',1,1)));p.send(w.message(layer,1,struct.pack('<I',5)));p.send(w.message(layer,2,struct.pack('<i',-1)));p.send(w.message(surf,6));p.sync()
end=time.monotonic()+2
while not p.configured and not p.closed and time.monotonic()<end:p.read()
if p.configured:
 p.send(w.message(layer,6,struct.pack('<I',p.serial)))
 fd=os.memfd_create('probe',os.MFD_CLOEXEC);os.write(fd,b'\0'*4)
 pool=p.new_id('pool');p.sock.sendmsg([w.message(shm,0,struct.pack('<Ii',pool,4))],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[fd]))]);os.close(fd)
 buf=p.new_id('buffer');p.send(w.message(pool,0,struct.pack('<IiiiiI',buf,0,1,1,4,0)))
 p.send(w.message(surf,1,struct.pack('<Iii',buf,0,0)));p.send(w.message(surf,2,struct.pack('<iiii',0,0,1,1)))
 cb=p.new_id('wl_callback');p.send(w.message(surf,3,struct.pack('<I',cb)));p.send(w.message(surf,6));p.sync();parsed=True
 p.sock.settimeout(1)
 try:
  while cb not in p.done_callbacks:p.read()
 except socket.timeout:pass
 print(json.dumps({'configured':p.configured,'closed':p.closed,'roundtrip':parsed,'frame':cb in p.done_callbacks}))
else:print(json.dumps({'configured':p.configured,'closed':p.closed}))
