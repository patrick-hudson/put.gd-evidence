import fcntl,os,struct,time,sys
f=os.open('/dev/uinput',os.O_WRONLY|os.O_NONBLOCK)
fcntl.ioctl(f,0x40045564,1)
for k in range(1,256):fcntl.ioctl(f,0x40045565,k)
fcntl.ioctl(f,0x405C5503,struct.pack('HHHH80sI',3,0x1234,0x5680,1,b'sfa15 lab keyboard',0));fcntl.ioctl(f,0x5501);time.sleep(1)
print('ready',flush=True)
def e(k,v):os.write(f,struct.pack('llHHi',0,0,1,k,v));os.write(f,struct.pack('llHHi',0,0,0,0,0))
try:
 for line in sys.stdin:
  if line.strip()=='q':break
  keys=list(map(int,line.split()))
  for k in keys:e(k,1)
  time.sleep(.05)
  for k in reversed(keys):e(k,0)
finally:fcntl.ioctl(f,0x5502);os.close(f)
