from pathlib import Path
import sys,json,time
root=Path('/home/patrick/work/putgd-a1275');sys.path.insert(0,str(root/'tools/lab'));import lab,rfb
r=root/'work/lab-runs/a4'
# Close setup UI without exiting the resident, then show a synthetic external window.
lab.pointer(r,1252,65,1280,800,True);lab.pointer(r,1252,65,1280,800,False)
print(lab.guest_session(r,"nohup xterm -bg '#ff00ff' -fg '#000000' -geometry 70x25+150+150 -T A1275-X11 -e sleep 600 >~/putgd-lab/witness.log 2>&1 </dev/null & echo $!\n"),flush=True)
time.sleep(3);lab.screenshot(r,'x11-witness')
for digit,name in [('2','window'),('3','desktop'),('1','region')]:
 lab.key(r,['ctrl','shift',digit]);time.sleep(2)
 lab.screenshot(r,'x11-'+name+'-hotkey')
 if name=='region':
  lab.pointer(r,220,220,1280,800,True)
  for i in range(1,11):lab.pointer(r,220+i*30,220+i*20,1280,800)
  lab.pointer(r,520,420,1280,800,False);time.sleep(3)
 data=lab.cli(r,'operation.recent');(r/('x11-'+name+'-operations.json')).write_text(json.dumps(data,indent=2))
 lab.screenshot(r,'x11-'+name+'-result')
 print(name,json.dumps(data),flush=True)
(r/'x11-final-capabilities.json').write_text(json.dumps(lab.cli(r,'capabilities'),indent=2))
print(lab.ssh(r,"find ~/putgd-lab/archive -type f -printf '%p %s bytes\\n'\n"),flush=True)
for name in ['published-tray-menu','x11-witness','x11-region-hotkey','x11-region-result']:
 c=rfb.RFB(5983);c.screenshot(r/(name+'-now.png'));c.close()
