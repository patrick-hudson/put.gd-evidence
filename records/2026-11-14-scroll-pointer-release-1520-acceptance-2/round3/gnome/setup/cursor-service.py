import json
from gi.repository import Gio,GLib
last=None
xml='<node><interface name="org.putgd.ScrollR2"><method name="Put"><arg type="s" direction="in"/></method><method name="Get"><arg type="s" direction="out"/></method></interface></node>'
def method(conn,sender,path,interface,name,params,invocation):
 global last
 if name=='Put':
  v=json.loads(params.unpack()[0]);assert len(v)==2;last=v;invocation.return_value(None)
 else:
  if last is None:invocation.return_dbus_error('org.putgd.ScrollR2.NotReady','No compositor cursor sample')
  else:invocation.return_value(GLib.Variant('(s)',(json.dumps(last),)))
def acquired(conn,name):
 conn.register_object('/Cursor',Gio.DBusNodeInfo.new_for_xml(xml).interfaces[0],method,None,None)
Gio.bus_own_name(Gio.BusType.SESSION,'org.putgd.ScrollR2',Gio.BusNameOwnerFlags.NONE,acquired,None,None)
GLib.MainLoop().run()
