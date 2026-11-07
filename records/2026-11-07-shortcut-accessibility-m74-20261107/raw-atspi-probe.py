"""Owned putgd-ui only, raw D-Bus, no Cache or libatspi calls."""
import dbus, dbus.bus, json, os, sys
from pathlib import Path
pid=int(sys.argv[1]);command=sys.argv[2]
session=dbus.SessionBus()
address=session.get_object('org.a11y.Bus','/org/a11y/bus').GetAddress(dbus_interface='org.a11y.Bus',timeout=3)
bus=dbus.bus.BusConnection(str(address)); A='org.a11y.atspi.Accessible'; P='org.freedesktop.DBus.Properties'
def obj(name,path):return bus.get_object(name,path,introspect=False)
def call(ref,interface,method,*args):return obj(*ref).get_dbus_method(method,interface)(*args,timeout=3)
def prop(ref,name):return call(ref,P,'Get',A,name)
registry=('org.a11y.atspi.Registry','/org/a11y/atspi/accessible/root')
roots=call(registry,A,'GetChildren'); owned=[]
for name,path in roots:
 actual=int(call(('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus','GetConnectionUnixProcessID',str(name)))
 if actual==pid:owned.append((str(name),str(path)))
assert owned, 'owned UI absent from accessibility registry'
rows=[];pending=owned[:];seen=set()
while pending:
 ref=pending.pop()
 if ref in seen:continue
 seen.add(ref)
 name=str(prop(ref,'Name'))
 # Do not query any text/value interface, or emit other controls' descriptions.
 row={'name':name,'path':ref[1],'bus':ref[0]};rows.append(row)
 pending += [(str(n),str(p)) for n,p in call(ref,A,'GetChildren') if str(p)!='/org/a11y/atspi/null']
if command=='list':print(json.dumps(rows,indent=2))
elif command=='click':
 wanted=sys.argv[3];found=[r for r in rows if r['name']==wanted];assert len(found)==1,found
 row=found[0];assert call((row['bus'],row['path']),'org.a11y.atspi.Action','DoAction',dbus.Int32(0))
elif command=='status':
 found=[r for r in rows if r['name']=='Shortcut recording status'];assert len(found)==1,found
 row=found[0];row['description']=str(prop((row['bus'],row['path']),'Description'));assert row['description'];row['pid']=pid
 print(json.dumps(row,ensure_ascii=False,indent=2))
