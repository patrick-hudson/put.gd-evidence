import time,struct
import wayland_toplevels as wire
from wayland_pointer import Pointer
p=Pointer(wire.socket_path(None));p.open();p.motion(400,300,1280,800);p.sync();time.sleep(.5);p.motion(640,350,1280,800);p.sync();time.sleep(.3);p.send(wire.message(p.pointer,5,struct.pack('<I',0)));p.send(wire.message(p.pointer,7,struct.pack('<IIii',p.stamp(),0,15*256,1)));p.send(wire.message(p.pointer,4));p.sync();print('virtual pointer bound, motion + wheel(15,1) sent');time.sleep(2);p.sock.close()
