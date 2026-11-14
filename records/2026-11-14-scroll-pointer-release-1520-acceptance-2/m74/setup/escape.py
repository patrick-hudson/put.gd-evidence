import os,fcntl,struct,time
from umouse import emit,UI_SET_EVBIT,UI_SET_KEYBIT,UI_DEV_SETUP,UI_DEV_CREATE,UI_DEV_DESTROY,EV_SYN,EV_KEY
fd=os.open('/dev/uinput',os.O_WRONLY|os.O_NONBLOCK)
try:
 fcntl.ioctl(fd,UI_SET_EVBIT,EV_KEY)
 for key in [1]:fcntl.ioctl(fd,UI_SET_KEYBIT,key)
 fcntl.ioctl(fd,UI_DEV_SETUP,struct.pack('HHHH80sI',3,0x1234,0x5680,1,b'putgd-lab escape',0));fcntl.ioctl(fd,UI_DEV_CREATE);time.sleep(1)
 for key in [1]:
  emit(fd,EV_KEY,key,1);emit(fd,EV_SYN,0,0);time.sleep(.05);emit(fd,EV_KEY,key,0);emit(fd,EV_SYN,0,0);time.sleep(.08)
finally:fcntl.ioctl(fd,UI_DEV_DESTROY);os.close(fd)
