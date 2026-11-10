import os,sys,json,urllib.parse
paths=['/tmp/pgbu','/tmp/pgl-000000/wayland-0','/tmp/pgl-000000/wrong-compositor','/tmp/pgl-000000/putgd/session.sock','/tmp/pg-vis-000000/display','/tmp/pg-peer-000000/display','/run/dbus/system_bus_socket']
for address in os.environ.get('DBUS_SESSION_BUS_ADDRESS','').split(';'):
 if address.startswith('unix:'):
  for field in address[5:].split(','):
   key,_,value=field.partition('=')
   if key in ('path','abstract'):paths.append(urllib.parse.unquote(value))
sizes={p:len(p.encode()) for p in paths};assert all(v<=107 for v in sizes.values())
print(json.dumps({'preflightSocketBytes':sizes,'temporarySuffix':'QTemporaryDir six-character suffix; representative equal-length names checked before test launch'}),flush=True)
os.execv(sys.argv[1],sys.argv[1:])
