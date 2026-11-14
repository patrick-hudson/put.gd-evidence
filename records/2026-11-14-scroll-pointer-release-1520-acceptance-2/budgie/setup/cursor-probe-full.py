from trial import Rfb,recvn
import struct,time,sys
r=Rfb(int(sys.argv[1]) if len(sys.argv)>1 else 5901);r.sock.settimeout(4);r.sock.sendall(struct.pack('>BxHiii',2,3,-239,-232,0));r.sock.sendall(struct.pack('>BBHHHH',3,0,0,0,r.width,r.height));seen=[]
try:
 for i in range(500):
  typ=recvn(r.sock,1)[0]
  if typ==0:
   n=struct.unpack('>xH',recvn(r.sock,3))[0]
   for _ in range(n):
    x,y,w,h,e=struct.unpack('>HHHHi',recvn(r.sock,12))
    if e==-232:seen.append([x,y]);print('POSITION',x,y,flush=True)
    elif e==0:recvn(r.sock,w*h*4)
    elif e==-239:recvn(r.sock,w*h*4+((w+7)//8)*h)
    else:raise RuntimeError('encoding '+str(e))
   r.sock.sendall(struct.pack('>BBHHHH',3,1,0,0,r.width,r.height))
   if len(seen)>3:break
  elif typ==2:pass
  elif typ==3:
   n=struct.unpack('>xxxI',recvn(r.sock,7))[0];recvn(r.sock,n)
  else:raise RuntimeError('message '+str(typ))
except Exception as e:print(type(e).__name__,str(e))
print('seen',seen)
