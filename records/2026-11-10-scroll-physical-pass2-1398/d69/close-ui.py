import pass2,json,os,time,subprocess
from pathlib import Path
P=pass2.P
desktop='plasmashell'
# Close only this isolated resident's dashboard by its owned PID, without killing it.
owned=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  if (proc/'comm').read_text().strip()=='putgd-ui' and ('XDG_CONFIG_HOME='+str(P/'c')).encode() in (proc/'environ').read_bytes().split(b'\0'):owned.append(int(proc.name))
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
if desktop=='plasmashell' and owned:
 js=P/'close-ui.js';js.write_text('for (const w of workspace.stackingOrder) { if ('+json.dumps(owned)+'.includes(w.pid)) w.closeWindow(); }')
 real=dict(os.environ,XDG_RUNTIME_DIR='/run/user/1000',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
 name='physical2-close-ui';i=subprocess.check_output(['qdbus6','org.kde.KWin','/Scripting','org.kde.kwin.Scripting.loadScript',str(js),name],env=real,text=True).strip()
 subprocess.run(['qdbus6','org.kde.KWin','/Scripting/Script'+i,'org.kde.kwin.Script.run'],env=real,capture_output=True);time.sleep(.5)
 subprocess.run(['qdbus6','org.kde.KWin','/Scripting','org.kde.kwin.Scripting.unloadScript',name],env=real,capture_output=True)
time.sleep(2)
