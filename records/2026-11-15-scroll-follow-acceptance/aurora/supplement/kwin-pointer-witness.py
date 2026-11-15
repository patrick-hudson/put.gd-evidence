"""Read KWin's documented workspace.cursorPos through a one-shot read-only script.
API https://develop.kde.org/docs/plasma/kwin/api/
Loading/receiver follows tools/lab/surface_driver/probe.py kwin_windows.
No input, surfaces, saved KWin configuration or product hooks.
"""
import json,os,tempfile
_cache=None
def get():
 import dbus,dbus.bus,dbus.service,dbus.mainloop.glib
 from gi.repository import GLib
 global _cache
 if _cache is None:
  bus=dbus.bus.BusConnection(dbus.bus.BUS_SESSION,mainloop=dbus.mainloop.glib.DBusGMainLoop());receiver='org.putgd.LabPointer.p%d'%os.getpid();_cache={'bus':bus,'receiver':receiver,'name':dbus.service.BusName(receiver,bus),'calls':0}
 c=_cache;c['calls']+=1;bus=c['bus'];path='/r%d'%c['calls'];loop=GLib.MainLoop();reply={}
 class Receiver(dbus.service.Object):
  @dbus.service.method('org.putgd.LabWitness',in_signature='s')
  def Report(self,text):reply['value']=json.loads(str(text));loop.quit()
 handler=Receiver(bus,path);plugin='sfa15-pointer-%d'%os.getpid()
 with tempfile.NamedTemporaryFile('w',suffix='.js',prefix='sfa15-pointer-',delete=False)as f:
  f.write('callDBus('+json.dumps(c['receiver'])+','+json.dumps(path)+',"org.putgd.LabWitness","Report",JSON.stringify([workspace.cursorPos.x,workspace.cursorPos.y]));');filename=f.name
 scripting=dbus.Interface(bus.get_object('org.kde.KWin','/Scripting'),'org.kde.kwin.Scripting');timeout=None
 try:
  identifier=int(scripting.loadScript(filename,plugin,signature='ss'));script=bus.get_object('org.kde.KWin','/Scripting/Script%d'%identifier);dbus.Interface(script,'org.kde.kwin.Script').run();timeout=GLib.timeout_add(3000,loop.quit);loop.run()
 finally:
  if timeout:
   try:GLib.source_remove(timeout)
   except Exception:pass
  scripting.unloadScript(plugin);os.unlink(filename);handler.remove_from_connection()
 assert 'value'in reply,'KWin cursor observer did not reply';return reply['value']
if __name__=='__main__':print(json.dumps(get()))
