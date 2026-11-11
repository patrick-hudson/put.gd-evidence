import os,sys,time,dbus,json
from pathlib import Path
p=Path('/home/patrick/work/p31398');e=json.loads((p/'env.json').read_text());os.environ.update(e)
b=dbus.SessionBus();o=b.get_object('org.gnome.Mutter.DisplayConfig','/org/gnome/Mutter/DisplayConfig');i='org.gnome.Mutter.DisplayConfig'
s,m,l,props=o.GetCurrentState(dbus_interface=i);scale=float(sys.argv[1]);connector=m[0][0][0];mode=next(x[0] for x in m[0][1] if x[6].get('is-current'))
config=dbus.Array([dbus.Struct((dbus.Int32(0),dbus.Int32(0),dbus.Double(scale),dbus.UInt32(0),dbus.Boolean(True),dbus.Array([dbus.Struct((connector,mode,dbus.Dictionary({},signature='sv')))],signature='(ssa{sv})')))],signature='(iiduba(ssa{sv}))')
o.ApplyMonitorsConfig(s,dbus.UInt32(1),config,dbus.Dictionary({},signature='sv'),dbus_interface=i);time.sleep(3)
print(str(o.GetCurrentState(dbus_interface=i)))
