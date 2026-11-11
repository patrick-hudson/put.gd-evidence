import pass2 as p,sys,subprocess,json,os,time
P=p.P;host=sys.argv[1];e=json.loads((P/'env.json').read_text());real=dict(e,XDG_RUNTIME_DIR='/run/user/1000')
if host=='m74':
 subprocess.run(['python3',str(P/'cinnamon_scale.py'),'snapshot'],check=True)
 try:
  subprocess.run(['python3',str(P/'cinnamon_scale.py'),'fractional'],check=True)
  subprocess.run(['python3',str(P/'cinnamon_scale.py'),'scale','1.5'],check=True)
  f=subprocess.Popen(['python3',str(P/'qt_fixture.py')],env=e,stdout=open(P/'scale-fixture.log','w'),stderr=subprocess.STDOUT)
  try:time.sleep(3);p.capture('scale150',scale=1.5)
  finally:f.terminate();f.wait(10)
 finally:subprocess.run(['python3',str(P/'cinnamon_scale.py'),'restore'],check=True)
elif host=='f44':
 os.environ.update(DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/1000/bus",XDG_RUNTIME_DIR="/run/user/1000")
 import dbus
 b=dbus.SessionBus();o=b.get_object('org.gnome.Mutter.DisplayConfig','/org/gnome/Mutter/DisplayConfig');iface='org.gnome.Mutter.DisplayConfig'
 state=o.GetCurrentState(dbus_interface=iface);old=float(state[2][0][2])
 (P/'scale-original.txt').write_text(str(state))
 try:
  subprocess.run(['python3',str(P/'gnome_scale.py'),'1.25'],check=True,env=e)
  p.batch('scaled',1)
 finally:subprocess.run(['python3',str(P/'gnome_scale.py'),str(old)],check=True,env=e)
else:
 state=json.loads(subprocess.check_output(['kscreen-doctor','-j'],env=real));(P/'scale-original.json').write_text(json.dumps(state,indent=2));o=next(x for x in state['outputs'] if x['enabled']);i=o['id'];old=o['scale']
 try:
  subprocess.run(['kscreen-doctor',f'output.{i}.scale.1.25'],env=real,check=True);time.sleep(3);p.batch('scaled',1)
 finally:subprocess.run(['kscreen-doctor',f'output.{i}.scale.{old}'],env=real,check=True)
