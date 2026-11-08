from pathlib import Path
import sys,time,json
root=Path('/home/patrick/work/putgd-a1275');sys.path.insert(0,str(root/'tools/lab'));import lab,rfb
r=root/'work/lab-runs/a3'
c=rfb.RFB(5982);c.click(600,400);c.close()
lab.key(r,['a']);lab.key(r,['ret'])
for k in ['f9','1','2','3']:lab.key(r,['ctrl','shift',k])
time.sleep(2);lab.screenshot(r,'magpie-seat-real-input')
c=rfb.RFB(5982);c.screenshot(r/'magpie-seat-real-input.png');c.close()
script='''python3 - <<'P'
from pathlib import Path
import json,os
out=Path('/tmp/magpie-seat')
result={'physicalTyping':Path('/tmp/magpie-seat-physical-input').read_text(),'fired':{k:Path('/tmp/magpie-a-'+k).exists() for k in ['F9','1','2','3']}}
(out/'real-input-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
P
XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0 wayland-info > /tmp/magpie-seat/globals.txt 2>&1
'''
print(lab.ssh(r,script),flush=True)
lab.ssh(r,'tar -C /tmp -czf /tmp/magpie-seat-evidence.tar.gz magpie-seat magpie-seat-physical-input\n');lab.get(r,'/tmp/magpie-seat-evidence.tar.gz',str(r/'magpie-seat-evidence.tar.gz'))
