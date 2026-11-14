import os,sys,json
from pathlib import Path
sys.path.insert(0,str(Path.home()/'work/w7-34'))
from proton_accept import desktop_environment
os.environ.update(desktop_environment()[1])
import dbus
js='JSON.stringify(Object.values(imports.ui.main.notificationDaemon._notifications).filter(n=>n.body==="The window could not be opened. Try opening it again from the tray.").map(n=>({id:n.id,summary:n.summary,body:n.body,sourcePid:n.notification?n.notification.source.pid:null,timestamp:n.notification?n.notification._timestamp.toISOString():null,expires:n.expires,urgency:n.hints.urgency,onScreen:n.notification===imports.ui.main.messageTray._notification,queueIndex:imports.ui.main.messageTray._notificationQueue.indexOf(n.notification)})))'
result=dbus.Interface(dbus.SessionBus().get_object('org.Cinnamon','/org/Cinnamon'),'org.Cinnamon').Eval(js)
value=json.loads(str(result[1])) if result[0] else str(result[1])
if result[0] and isinstance(value,str):value=json.loads(value)
out={'success':bool(result[0]),'matchingNotifications':value}
(Path.home()/'work/w7-34/toast-server-metadata.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'success':out['success'],'count':len(value),'newestKnownTimestamp':max(n['timestamp'] or '' for n in value),'onScreen':[n for n in value if n['onScreen']]},indent=2))
