"""Drive the real resident's exported StatusNotifierItem, never a mock host."""
from gi.repository import Gio,GLib
import os,pathlib

def call(bus,name,path,interface,method,signature=None,values=None):
 p=GLib.Variant(signature,values) if signature else None
 return bus.call_sync(name,path,interface,method,p,None,Gio.DBusCallFlags.NONE,5000,None).unpack()

def service_for(pid):
 bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
 def descendants(p):
  try: children=[int(v) for v in (pathlib.Path('/proc')/str(p)/'task'/str(p)/'children').read_text().split()]
  except FileNotFoundError: return []
  return children+[v for c in children for v in descendants(c)]
 owned={pid,*descendants(pid)}; matches=[]
 for name in call(bus,'org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','ListNames')[0]:
  if name.startswith('org.kde.StatusNotifierItem.putgd_'):
   owner=call(bus,'org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','GetConnectionUnixProcessID','(s)',(name,))[0]
   if owner in owned: matches.append(name)
 assert len(matches)==1,matches
 return bus,matches[0]

def activate(pid,label):
 bus,name=service_for(pid)
 layout=call(bus,name,'/Menu','com.canonical.dbusmenu','GetLayout','(iias)',(0,-1,[]))[1]
 found=[]
 def visit(node):
  if hasattr(node,'unpack'): node=node.unpack()
  ident,props,children=node
  if props.get('label','').replace('&','')==label: found.append(ident)
  for child in children: visit(child)
 visit(layout); assert len(found)==1,(label,found)
 call(bus,name,'/Menu','com.canonical.dbusmenu','Event','(isvu)',(found[0],'clicked',GLib.Variant('s',''),0))
 return {'service':name,'menuId':found[0],'label':label}
