import ctypes,subprocess,time,os,json
import gi
from pathlib import Path
from PIL import Image
import numpy as np
gi.require_version('Gst','1.0'); from gi.repository import Gst
Gst.init(None)
out=Path(os.environ['OUT']); out.mkdir(parents=True,exist_ok=True)
x=ctypes.CDLL('libX11.so.6'); xt=ctypes.CDLL('libXtst.so.6'); x.XOpenDisplay.restype=ctypes.c_void_p; d=x.XOpenDisplay(None)
xt.XTestFakeMotionEvent.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ulong]; xt.XTestFakeButtonEvent.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_int,ctypes.c_ulong]; x.XFlush.argtypes=[ctypes.c_void_p]
x.XDefaultRootWindow.argtypes=[ctypes.c_void_p];x.XDefaultRootWindow.restype=ctypes.c_ulong
root=x.XDefaultRootWindow(d);retroot=ctypes.c_ulong();child=ctypes.c_ulong();rx=ctypes.c_int();ry=ctypes.c_int();wx=ctypes.c_int();wy=ctypes.c_int();mask=ctypes.c_uint()
x.XQueryPointer.argtypes=[ctypes.c_void_p,ctypes.c_ulong,*([ctypes.c_void_p]*7)]
if not x.XQueryPointer(d,root,ctypes.byref(retroot),ctypes.byref(child),ctypes.byref(rx),ctypes.byref(ry),ctypes.byref(wx),ctypes.byref(wy),ctypes.byref(mask)):raise RuntimeError('cannot save pointer')
if mask.value & (1|4|8|64):raise RuntimeError('release Shift/Ctrl/Alt/Super before probing')
p=Gst.parse_launch('ximagesrc show-pointer=false use-damage=false startx=0 starty=150 endx=1799 endy=749 ! queue leaky=downstream max-size-buffers=2 ! videoconvert ! video/x-raw,format=RGB ! appsink name=tap max-buffers=2 drop=true sync=false'); tap=p.get_by_name('tap'); p.set_state(Gst.State.PLAYING)
def frame():
 sample=tap.emit('try-pull-sample',3*Gst.SECOND)
 if sample is None: raise RuntimeError('no frame')
 caps=sample.get_caps().get_structure(0); w=caps.get_value('width'); h=caps.get_value('height'); buf=sample.get_buffer(); ok,m=buf.map(Gst.MapFlags.READ); data=np.frombuffer(m.data,dtype=np.uint8).reshape(h,-1)[:,:w*3].reshape(h,w,3).copy(); buf.unmap(m); return data
try:
 xt.XTestFakeMotionEvent(d,-1,400,400,0); x.XFlush(d); time.sleep(1); frame(); time.sleep(.2); a=frame(); Image.fromarray(a).save(out/'before.png')
 xt.XTestFakeButtonEvent(d,5,1,0); xt.XTestFakeButtonEvent(d,5,0,0); x.XFlush(d); time.sleep(2); frame(); time.sleep(.2); b=frame(); Image.fromarray(b).save(out/'after.png')
 candidates=[]
 for dy in range(1,min(400,a.shape[0]-25)):
  diff=np.abs(a[dy:].astype(np.int16)-b[:-dy].astype(np.int16)); candidates.append((float(diff.mean()),dy,int(diff.max()),int(np.all(diff==0,axis=(1,2)).sum())))
 print(json.dumps({'frame':list(a.shape),'best':sorted(candidates)[:5]}))
finally:
 p.set_state(Gst.State.NULL);xt.XTestFakeMotionEvent(d,-1,rx.value,ry.value,0);x.XFlush(d)
