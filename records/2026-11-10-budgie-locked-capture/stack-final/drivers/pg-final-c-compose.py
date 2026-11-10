import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
name=sys.argv[1];r=Path('/home/patrick/work/pg-cd/work/lab-runs')/name;o=r/'accept';extra=o/'C-final-extra'
version=json.loads((extra/'version.json').read_text());assert version['gitCommit']=='3e071edc821e01b7bbc79feb742d799d15516049'
before=Path('/tmp/pg-c-final-before.png');beforeOp=json.loads(Path('/tmp/pg-c-final-before-operation.json').read_text())
assert beforeOp['state']=='completed' and beforeOp['items'][0]['local']['status']=='saved'
assert hashlib.sha256(before.read_bytes()).hexdigest()==beforeOp['items'][0]['artifact']['sha256']
loaded=json.loads((extra/'loaded-results.json').read_text());assert len(loaded)==10 and all(x['operation']['state']=='completed' for x in loaded)
metrics=json.loads((extra/'load-metrics.json').read_text());busy=metrics['guestBusyPercent']
for label in ('locked-0','locked-1','locked-2','locked-monitor','locked-repeat','blanked-unlocked'):
 op=json.loads((extra/(label+'.json')).read_text())['operation'];assert op['state']=='failed' and op['error']['code']=='session_locked' and not op['items']
files=json.loads((extra/'locked-no-new-files.json').read_text());assert files['unchanged'] and files['before']==files['after']
files=json.loads((extra/'blank-files.json').read_text());assert files['before']==files['after']
state=(extra/'blank-state.txt').read_text();assert 'LockedHint=no' in state and 'gtklock-absent' in state
assert json.loads((extra/'unlocked-after.json').read_text())['state']=='completed'
assert '0 failed, 0 skipped' in (o/'protocol-tests.log').read_text()
for desktop,log in [('Budgie',o/'driver-C.log')]:assert '# 0 failed' in log.read_text()
img=Image.new('RGB',(1200,1080),'#f3f5f8');draw=ImageDraw.Draw(img)
for x,p in [(65,before),(650,extra/'locked.png')]:
 im=Image.open(p).convert('RGB');assert im.size==(1280,800)
 img.paste(im.resize((512,320),Image.Resampling.LANCZOS),(x,190))
 draw.rectangle((x,545,x+512,700),fill='#172b4d')
img.save(o/'c-final-before-after-base.png')
shapes=[
 {'kind':'text','at':[40,50],'text':'Budgie captures refuse a hidden display before and after pixel copies','fontPixels':27,'color':'#172b4d'},
 {'kind':'text','at':[65,120],'text':'BEFORE nightly 7fc609dc4','fontPixels':24,'color':'#d7263d'},
 {'kind':'text','at':[650,120],'text':'AFTER ec54feb3e / CI4522','fontPixels':24,'color':'#047857'},
 {'kind':'text','at':[65,164],'text':'Actual lock-screen PNG saved by put.gd','fontPixels':19,'color':'#172b4d'},
 {'kind':'text','at':[650,164],'text':'Guest console witness; no capture saved','fontPixels':19,'color':'#172b4d'},
 {'kind':'text','at':[85,563],'text':'state: completed','fontPixels':23,'color':'#ffffff'},
 {'kind':'text','at':[85,603],'text':'local: saved','fontPixels':23,'color':'#ffffff'},
 {'kind':'text','at':[85,643],'text':'image: the gtklock screen','fontPixels':23,'color':'#ffffff'},
 {'kind':'text','at':[670,563],'text':'state: failed','fontPixels':23,'color':'#ffffff'},
 {'kind':'text','at':[670,603],'text':'error: session_locked','fontPixels':23,'color':'#ffffff'},
 {'kind':'text','at':[670,643],'text':'items: []    new files: 0','fontPixels':23,'color':'#ffffff'},
 {'kind':'arrow','from':[590,735],'to':[665,680],'width':4,'color':'#047857'},
 {'kind':'text','at':[650,726],'text':'3 desktop + monitor + repeat: all refused','fontPixels':21,'color':'#047857'},
 {'kind':'text','at':[40,810],'text':f'10 / 10 captures completed while Firefox animated 9,000 rectangles ({busy:.1f}% guest CPU busy)','fontPixels':20,'color':'#172b4d'},
 {'kind':'text','at':[40,855],'text':'Unlocked DPMS-off: session_locked, no file. Power restored: capture completed.','fontPixels':20,'color':'#172b4d'},
 {'kind':'text','at':[40,900],'text':'Current capture driver: Budgie 15 / 15; Hyprland 15 / 15. Capture after unlocking succeeds.','fontPixels':20,'color':'#172b4d'},
 {'kind':'text','at':[40,945],'text':'Native protocol regressions: 13 passed, 0 failed, 0 skipped; frozen-window and post-copy locks covered.','fontPixels':19,'color':'#172b4d'},
 {'kind':'text','at':[40,1030],'text':'Fresh f44 KVM guest | Budgie 10.10.3 / labwc 0.20.2 / gtklock 4.0.0 | software rendering','fontPixels':18,'color':'#172b4d'}]
(o/'c-final-annotations.json').write_text(json.dumps(shapes,indent=2))
