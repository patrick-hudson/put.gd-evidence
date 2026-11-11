import os,json,signal
from pathlib import Path
from gi.repository import Gio,GLib
P=Path('/home/patrick/work/sr8');os.environ['DBUS_SESSION_BUS_ADDRESS']='unix:path=/run/user/1000/bus';b=Gio.bus_get_sync(Gio.BusType.SESSION,None)
def db(m,args):return b.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus',m,args,None,Gio.DBusCallFlags.NONE,3000,None).unpack()
name='org.freedesktop.Notifications';before=db('GetNameOwner',GLib.Variant('(s)',(name,)));result=db('RequestName',GLib.Variant('(su)',(name,6)));(P/'fallback-owner.json').write_text(json.dumps({'before':before,'request':result}))
if result!=(1,):raise RuntimeError('Notification server does not allow replacement; unchanged')
xml='<node><interface name="org.freedesktop.Notifications"><method name="GetCapabilities"><arg type="as" direction="out"/></method><method name="GetServerInformation"><arg type="s" direction="out"/><arg type="s" direction="out"/><arg type="s" direction="out"/><arg type="s" direction="out"/></method><method name="Notify"><arg type="s" direction="in"/><arg type="u" direction="in"/><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="as" direction="in"/><arg type="a{sv}" direction="in"/><arg type="i" direction="in"/><arg type="u" direction="out"/></method><method name="CloseNotification"><arg type="u" direction="in"/></method></interface></node>'
def called(conn,sender,path,interface,method,args,invocation):
 with (P/'fallback-calls.jsonl').open('a') as f:f.write(json.dumps({'method':method})+'\n')
 if method=='GetCapabilities':invocation.return_value(GLib.Variant('(as)',([],)))
 elif method=='GetServerInformation':invocation.return_value(GLib.Variant('(ssss)',('Fallback test','putgd test','1','1.2')))
 else:invocation.return_dbus_error('org.freedesktop.DBus.Error.UnknownMethod','No notification daemon answer for the fallback test')
b.register_object('/org/freedesktop/Notifications',Gio.DBusNodeInfo.new_for_xml(xml).interfaces[0],called,None,None);(P/'fallback-server.ready').touch();loop=GLib.MainLoop()
def stop(*_):db('ReleaseName',GLib.Variant('(s)',(name,)));loop.quit()
signal.signal(signal.SIGTERM,stop);loop.run();(P/'fallback-restored-owner.json').write_text(json.dumps(db('GetNameOwner',GLib.Variant('(s)',(name,)))))
