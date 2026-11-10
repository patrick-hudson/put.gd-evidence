import dbus,dbus.mainloop.glib,json,time,os
from gi.repository import GLib
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus=dbus.SessionBus(); rd='org.gnome.Mutter.RemoteDesktop'; sc='org.gnome.Mutter.ScreenCast'; rdi=rd+'.Session'; sci=sc+'.Session'
rpath=bus.get_object(rd,'/org/gnome/Mutter/RemoteDesktop').CreateSession(dbus_interface=rd)
r=bus.get_object(rd,rpath); sid=r.Get(rdi,'SessionId',dbus_interface='org.freedesktop.DBus.Properties')
spath=bus.get_object(sc,'/org/gnome/Mutter/ScreenCast').CreateSession(dbus.Dictionary({'remote-desktop-session-id':sid},signature='sv'),dbus_interface=sc)
scale=float(os.environ.get('SCALE','1'));s=bus.get_object(sc,spath); stream=s.RecordArea(dbus.Int32(0),dbus.Int32(int(150/scale)),dbus.Int32(int(1800/scale)),dbus.Int32(int(600/scale)),dbus.Dictionary({'cursor-mode':dbus.UInt32(0)},signature='sv'),dbus_interface=sci)
if os.environ.get('MONITOR'):stream=s.RecordMonitor('HDMI-1',dbus.Dictionary({'cursor-mode':dbus.UInt32(0)},signature='sv'),dbus_interface=sci)
import gi
gi.require_version('Gst','1.0'); from gi.repository import Gst
from PIL import Image
import numpy as np
from pathlib import Path
Gst.init(None); pipe=None
out=Path(os.environ.get('OUT','frames'));out.mkdir(parents=True,exist_ok=True)
def frame(name):
 sample=pipe.get_by_name('tap').emit('try-pull-sample',3*Gst.SECOND)
 if sample is None:raise RuntimeError('no pipewire frame')
 caps=sample.get_caps().get_structure(0);w=caps.get_value('width');h=caps.get_value('height');buf=sample.get_buffer();ok,m=buf.map(Gst.MapFlags.READ);a=np.frombuffer(m.data,dtype=np.uint8).reshape(h,-1)[:,:w*3].reshape(h,w,3).copy();buf.unmap(m);Image.fromarray(a).save(out/(name+'.png'));print(json.dumps({'frame':name,'size':[w,h]}),flush=True)
loop=GLib.MainLoop()
def node(n):
 global pipe
 print(json.dumps({'node':int(n),'stage':'stream-added'}),flush=True)
 pipe=Gst.parse_launch(f'pipewiresrc path={int(n)} ! queue leaky=downstream max-size-buffers=2 ! videoconvert ! video/x-raw,format=RGB ! appsink name=tap max-buffers=2 drop=true sync=false');pipe.set_state(Gst.State.PLAYING)
 GLib.timeout_add(1000,inject)
def inject():
 try:
  if not os.environ.get('INPUT_ONLY'):frame('before')
  r.NotifyPointerMotionAbsolute(str(stream),dbus.Double(300),dbus.Double(200),dbus_interface=rdi);
  if os.environ.get('RELATIVE'):r.NotifyPointerMotionRelative(dbus.Double(400),dbus.Double(350),dbus_interface=rdi)
  time.sleep(0.3); r.NotifyPointerMotionAbsolute(str(stream),dbus.Double(300),dbus.Double(200),dbus_interface=rdi); time.sleep(0.3); r.NotifyPointerAxisDiscrete(dbus.UInt32(0),dbus.Int32(1),dbus_interface=rdi);print('MOTION_AND_AXIS_OK',flush=True)
 except Exception as e: print(str(e),flush=True)
 GLib.timeout_add(3000,after);return False
def after():
 if not os.environ.get('INPUT_ONLY'):frame('after')
 finish();return False
def finish():
 if pipe:pipe.set_state(Gst.State.NULL)
 r.Stop(dbus_interface=rdi);loop.quit();return False
bus.add_signal_receiver(node,signal_name='PipeWireStreamAdded',dbus_interface=sc+'.Stream',path=str(stream))
try:
 r.Start(dbus_interface=rdi);print('LINKED_START_OK',flush=True);GLib.timeout_add(20000,finish);loop.run()
finally:
 try:r.Stop(dbus_interface=rdi)
 except Exception:pass
