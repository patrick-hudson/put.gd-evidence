import os,sys,json,time,datetime
from pathlib import Path
sys.path.insert(0,str(Path.home()/'work/w7-34'))
from proton_accept import desktop_environment
import desktop_lock
state=desktop_lock.Desktop(Path.home()/'putgd-lab/locks','m74').status();assert state.get('state')=='held' and state.get('lock',{}).get('session')=='w7-toast-clean'
os.environ.update(desktop_environment()[1])
import dbus
bus=dbus.SessionBus();shell=dbus.Interface(bus.get_object('org.Cinnamon','/org/Cinnamon'),'org.Cinnamon');service=dbus.Interface(bus.get_object('org.freedesktop.Notifications','/org/freedesktop/Notifications'),'org.freedesktop.Notifications')
message='The window could not be opened. Try opening it again from the tray.'
js='JSON.stringify(Object.values(imports.ui.main.notificationDaemon._notifications).filter(n=>n.appName==="put.gd"&&n.body==='+json.dumps(message)+').map(n=>({id:n.id,application:n.appName,text:n.body,sourcePid:n.notification?n.notification.source.pid:null,timestamp:n.notification?n.notification._timestamp.toISOString():null,expires:n.expires,urgency:n.hints.urgency})))'
def query():
 ok,value=shell.Eval(js);assert ok
 value=json.loads(str(value));return json.loads(value) if isinstance(value,str) else value
before=query();assert len(before)==81
cutoff='2026-11-13T20:00:00.000Z'
for row in before:
 assert row['application']=='put.gd' and row['text']==message
 if row['timestamp']:
  assert row['timestamp']<cutoff;row['ageBasis']='notification timestamp before earliest W7 runs'
 else:
  # Same daemon allocates monotonically with nextNotificationId++ (notificationDaemon.js:336).
  # An unmaterialized record has no Notification timestamp; a later timestamped
  # matching id bounds its creation before that old timestamp, without inventing one.
  upper=min((r for r in before if r['id']>row['id'] and r['timestamp']),key=lambda r:r['id'])
  assert upper['timestamp']<cutoff
  row['ageBasis']={'inferredFromSameDaemonMonotonicId':True,'laterId':upper['id'],'laterTimestamp':upper['timestamp']}
for row in before:service.CloseNotification(dbus.UInt32(row['id']))
end=time.monotonic()+5
while True:
 after=query()
 if not after or time.monotonic()>end:break
 time.sleep(.1)
assert not after
out={'recordedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'closedCount':len(before),'remainingExactMatchCount':len(after),'method':'org.freedesktop.Notifications.CloseNotification, one guarded call per id','cutoffBeforeEarliestW7Runs':cutoff,'closed':before,'everyOtherNotificationLeftAlone':True}
(Path.home()/'work/w7-34/toast-cleanup.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'closedCount':len(before),'remainingExactMatchCount':0,'withoutMaterializedTimestamp':[r['id'] for r in before if not r['timestamp']],'earliestTimestamp':min(r['timestamp'] for r in before if r['timestamp']),'latestTimestamp':max(r['timestamp'] for r in before if r['timestamp'])}))
