from trial import Rfb,recvn
import struct,time
r=Rfb(5901);r.sock.settimeout(4);r.sock.sendall(struct.pack('>BxHii',2,2,-232,0));r.sock.sendall(struct.pack('>BBHHHH',3,0,0,0,r.width,r.height));seen=[]
try:
 for i in range(100):
  typ=recvn(r.sock,1)[0]
  if typ==0:
   n=struct.unpack('>xH',recvn(r.sock,3))[0]
   for _ in range(n):
    x,y,w,h,e=struct.unpack('>HHHHi',recvn(r.sock,12))
    if e==-232:seen.append([x,y]);print('POSITION',x,y,flush=True)
    elif e==0:recvn(r.sock,w*h*4)
    else:raise RuntimeError('encoding '+str(e))
   r.sock.sendall(struct.pack('>BBHHHH',3,1,0,0,r.width,r.height))
   if len(seen)>3:break
  elif typ==2:pass
  elif typ==3:
   n=struct.unpack('>xxxI',recvn(r.sock,7))[0];recvn(r.sock,n)
  else:raise RuntimeError('message '+str(typ))
except Exception as e:print(type(e).__name__,str(e))
print('seen',seen)
