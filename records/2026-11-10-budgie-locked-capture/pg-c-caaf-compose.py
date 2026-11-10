from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
r=Path('/home/patrick/work/pg-cd/work/lab-runs/bc6');out=r/'accept'
img=Image.new('RGB',(1300,850),'#f3f5f8');d=ImageDraw.Draw(img)
for x,src in [(55,'/tmp/pg-c-before-locked.png'),(705,out/'locked.png')]:
 shot=Image.open(src).convert('RGB');shot.thumbnail((540,338));img.paste(shot,(x,175));d.rectangle((x,535,x+540,705),fill='#172b4d')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',18)
before=['action.invoke {action: desktop}', 'state: completed', 'items: 1  (lock-screen PNG saved)']
op=json.loads((out/'locked-0.json').read_text());assert op['error']['code']=='session_locked'
after=['action.invoke {action: desktop}', 'state: '+op['state'], 'error.code: '+op['error']['code'],'items: 0; new files: 0 (3 / 3)']
for x,lines in [(70,before),(720,after)]:
 for i,line in enumerate(lines):d.text((x,550+i*34),line,font=font,fill='white')
img.save(out/'c-before-after-base.png')
shapes=[{'kind':'text','at':[40,53],'text':'Budgie: refuse screen reads while gtklock covers the session','fontPixels':28,'color':'#172b4d'},
 {'kind':'text','at':[55,128],'text':'BEFORE nightly 7fc609dc4','fontPixels':25,'color':'#d7263d'},
 {'kind':'text','at':[705,128],'text':'AFTER head caaf7628c','fontPixels':25,'color':'#047857'},
 {'kind':'text','at':[55,733],'text':'Captured the lock screen','fontPixels':21,'color':'#d7263d'},
 {'kind':'text','at':[705,733],'text':'Same real gtklock; capture refused','fontPixels':21,'color':'#047857'},
 {'kind':'arrow','from':[1200,515],'to':[1055,628],'width':4,'color':'#d7263d'},
 {'kind':'text','at':[40,786],'text':'Exact CI AppImage merge c20025120941 / PR head caaf7628c','fontPixels':20,'color':'#172b4d'},
 {'kind':'text','at':[40,821],'text':'Cold first capture: pass | real gtklock: 3 / 3 refused | after unlock: pass | fresh d69 guest','fontPixels':19,'color':'#172b4d'}]
(out/'c-annotations.json').write_text(json.dumps(shapes))
