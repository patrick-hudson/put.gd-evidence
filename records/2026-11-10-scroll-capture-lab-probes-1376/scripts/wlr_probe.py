import os,sys,time,struct,socket,array,mmap,zlib,json
from pathlib import Path
import wayland_toplevels as wire
from wayland_pointer import Pointer
P=struct.pack
class Capture(wire.Client):
 def dispatch(self,obj,op,r):
  kind=self.objects.get(obj)
  if kind=='session':
   if op==0:self.w,self.h=r.uint(),r.uint()
   if op==1:self.formats.append(r.uint())
   if op==4:self.constraints=True
   if op==5:raise RuntimeError('capture stopped')
  elif kind=='frame':
   if op==0:self.transform=r.uint()
   if op==3:self.ready=True
   if op==4:raise RuntimeError('capture failed '+str(r.uint()))
  elif kind in ['wl_registry','wl_display','wl_callback']:super().dispatch(obj,op,r)
 def open(self):
  self.registry=self.new_id('wl_registry');self.send(wire.message(1,1,P('<I',self.registry)));self.sync()
  print(json.dumps({'protocols':self.globals}),flush=True)
  ids={}
  for interface,kind in [('wl_output','output'),('wl_shm','shm'),('ext_output_image_capture_source_manager_v1','source_manager'),('ext_image_copy_capture_manager_v1','manager')]:
   self.bind(interface,1,kind);ids[kind]=self.next_id-1
  source=self.new_id('source');self.send(wire.message(ids['source_manager'],0,P('<II',source,ids['output'])))
  self.session=self.new_id('session');self.formats=[];self.constraints=False
  self.send(wire.message(ids['manager'],0,P('<III',self.session,source,int(os.environ.get('CURSOR','0')))))
  while not self.constraints:self.read()
  print(json.dumps({'size':[self.w,self.h],'formats':self.formats}),flush=True)
  fmt=1 if 1 in self.formats else self.formats[0]
  if fmt not in (0,1,875713112,875709016):raise RuntimeError('unsupported shm format '+str(fmt))
  self.fmt=fmt
  self.fd=os.memfd_create('scrollprobe');os.ftruncate(self.fd,self.w*self.h*4);self.mem=mmap.mmap(self.fd,self.w*self.h*4)
  pool=self.new_id('pool');self.sock.sendmsg([wire.message(ids['shm'],0,P('<Ii',pool,self.w*self.h*4))],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[self.fd]))])
  self.buf=self.new_id('buffer');self.send(wire.message(pool,0,P('<IiiiiI',self.buf,0,self.w,self.h,self.w*4,fmt)));self.sync()
 def frame(self,path):
  f=self.new_id('frame');self.ready=False;self.transform=0
  self.send(wire.message(self.session,0,P('<I',f)));self.send(wire.message(f,1,P('<I',self.buf)));self.send(wire.message(f,2,P('<iiii',0,0,self.w,self.h)));self.send(wire.message(f,3))
  deadline=time.monotonic()+8
  while not self.ready:
   if time.monotonic()>deadline:raise TimeoutError('no frame ready within 8s')
   self.read()
  if self.transform:raise RuntimeError('unhandled output transform '+str(self.transform))
  data=self.mem[:];raw=bytearray()
  for y in range(self.h):
   row=data[y*self.w*4:(y+1)*self.w*4];rgb=bytearray(self.w*3);rgb[0::3]=row[0::4] if self.fmt==875709016 else row[2::4];rgb[1::3]=row[1::4];rgb[2::3]=row[2::4] if self.fmt==875709016 else row[0::4];raw+=b'\0'+rgb
  def chunk(t,d):return P('>I',len(d))+t+d+P('>I',zlib.crc32(t+d))
  Path(path).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',P('>IIBBBBB',self.w,self.h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
  self.send(wire.message(f,0));self.sync();return data
out=Path(os.environ['OUT']);out.mkdir(parents=True,exist_ok=True)
c=Capture(wire.socket_path(None),timeout=8);c.open();p=Pointer(wire.socket_path(None));p.open();p.motion(400,300,c.w,c.h);p.sync();time.sleep(.5);c.frame(out/'warmup.png');time.sleep(2);a=c.frame(out/'before.png')
p.send(wire.message(p.pointer,5,P('<I',0))) # wheel source
p.send(wire.message(p.pointer,7,P('<IIii',p.stamp(),0,15*256,1)));p.send(wire.message(p.pointer,4));p.sync();time.sleep(2);b=c.frame(out/'after.png')
print(json.dumps({'changed':a!=b,'frame':[c.w,c.h]}),flush=True);p.sock.close();c.sock.close()
