import dbus,os,subprocess,time
from pathlib import Path
bus=dbus.SessionBus();d=bus.get_object('org.gnome.Mutter.DisplayConfig','/org/gnome/Mutter/DisplayConfig');iface='org.gnome.Mutter.DisplayConfig'
def apply(scale):
 serial,monitors,logical,props=d.GetCurrentState(dbus_interface=iface);m=monitors[0];connector=m[0][0];mode=next(mode[0] for mode in m[1] if mode[6].get('is-current'))
 config=dbus.Array([dbus.Struct((dbus.Int32(0),dbus.Int32(0),dbus.Double(scale),dbus.UInt32(0),dbus.Boolean(True),dbus.Array([dbus.Struct((connector,mode,dbus.Dictionary({},signature='sv')))],signature='(ssa{sv})')))],signature='(iiduba(ssa{sv}))')
 d.ApplyMonitorsConfig(serial,dbus.UInt32(1),config,dbus.Dictionary({},signature='sv'),dbus_interface=iface);time.sleep(3)
root=Path(__file__).parent
try:
 for scale in [1,1.25,2]:
  apply(scale);env=os.environ.copy();env['SCALE']=str(scale);env['OUT']=str(root/('gnome-browser-'+str(scale)));subprocess.run(['python3',str(root/'mutter_probe.py')],env=env,check=True);subprocess.run(['python3',str(root/'compare.py'),env['OUT']],check=True)
finally:apply(1)
