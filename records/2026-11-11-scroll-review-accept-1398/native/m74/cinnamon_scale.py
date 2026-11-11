#!/usr/bin/python3
"""Run on the locked Cinnamon builder; uses Muffin's display-settings API."""
import os,sys,json,time,subprocess
from pathlib import Path
os.environ.update(DISPLAY=':0',XAUTHORITY='/home/patrick/.Xauthority',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
import gi
gi.require_version('Gio','2.0');from gi.repository import Gio,GLib
out=Path('/home/patrick/work/sr8/cscale');out.mkdir(mode=0o700,exist_ok=True)
bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
def call(method,args=None):
 return bus.call_sync('org.cinnamon.Muffin.DisplayConfig','/org/cinnamon/Muffin/DisplayConfig','org.cinnamon.Muffin.DisplayConfig',method,args,None,Gio.DBusCallFlags.NONE,10000,None).unpack()
def state():
 s=call('GetCurrentState'); print(json.dumps(s,indent=2));return s
def apply(scale):
 serial,monitors,logical,props=call('GetCurrentState')
 configs=[]
 for xx,yy,old,transform,primary,ids,lp in logical:
  entries=[]
  for ident in ids:
   monitor=next(m for m in monitors if m[0]==ident)
   mode=next(m for m in monitor[1] if m[6].get('is-current'))
   entries.append((ident[0],mode[0],{}))
  configs.append((xx,yy,scale,transform,primary,entries))
 call('ApplyMonitorsConfig',GLib.Variant('(uua(iiduba(ssa{sv}))a{sv})',(serial,1,configs,{})))
 time.sleep(3);state()
cmd=sys.argv[1]
if cmd=='snapshot':
 data={}
 for schema,key in [('org.cinnamon.desktop.interface','scaling-factor'),('org.cinnamon.settings-daemon.plugins.xsettings','overrides'),('org.cinnamon.muffin','experimental-features'),('org.cinnamon.muffin.x11','fractional-scale-mode')]:
  data[schema+'/'+key]=subprocess.check_output(['gsettings','get',schema,key],text=True).strip()
 data['state']=call('GetCurrentState');data['monitors_exists']=(Path.home()/'.config/monitors.xml').exists()
 if data['monitors_exists']: (out/'monitors.xml.original').write_bytes((Path.home()/'.config/monitors.xml').read_bytes())
 (out/'original.json').write_text(json.dumps(data,indent=2));state()
elif cmd=='state': state()
elif cmd=='scale': apply(float(sys.argv[2]))
elif cmd=='fractional':
 s=Gio.Settings.new('org.cinnamon.muffin');features=s.get_strv('experimental-features')
 for f in ['scale-monitor-framebuffer','x11-randr-fractional-scaling']:
  if f not in features:features.append(f)
 s.set_strv('experimental-features',features);Gio.Settings.sync();time.sleep(3);state()
elif cmd=='restore':
 data=json.loads((out/'original.json').read_text());apply(data['state'][2][0][2])
 for name,value in data.items():
  if '/' in name: schema,key=name.split('/');subprocess.run(['gsettings','set',schema,key,value],check=True)
 dest=Path.home()/'.config/monitors.xml'
 if data['monitors_exists']:dest.write_bytes((out/'monitors.xml.original').read_bytes())
 elif dest.exists():dest.unlink()
 time.sleep(3);state()
