import dbus,dbus.service,dbus.mainloop.glib,json,sys
from gi.repository import GLib
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
class Peer(dbus.service.Object):
 @dbus.service.method('org.freedesktop.Notifications',in_signature='',out_signature='ssss')
 def GetServerInformation(self):return ('putgd scroll test','putgd','1','1.2')
 @dbus.service.method('org.freedesktop.Notifications',in_signature='',out_signature='as')
 def GetCapabilities(self):return ['body']
 @dbus.service.method('org.freedesktop.Notifications',in_signature='susssasa{sv}i',out_signature='u')
 def Notify(self,app,replace,icon,summary,body,actions,hints,timeout):
  with open(sys.argv[1],'a') as f:f.write(json.dumps({'summary':str(summary),'body':str(body),'urgency':int(hints.get('urgency',1))})+'\n')
  return 1
 @dbus.service.method('org.freedesktop.Notifications',in_signature='u',out_signature='')
 def CloseNotification(self,id):pass
bus=dbus.SessionBus();name=dbus.service.BusName('org.freedesktop.Notifications',bus);peer=Peer(bus,'/org/freedesktop/Notifications');GLib.MainLoop().run()
