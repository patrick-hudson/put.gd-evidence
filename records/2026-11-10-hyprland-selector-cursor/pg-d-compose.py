from PIL import Image,ImageDraw
from pathlib import Path
import json
r=Path('/home/patrick/work/pg-cd/work/lab-runs/hc3')
before=Image.open('/tmp/pg-d-before14.png').convert('RGB');after=Image.open(r/'repro-after/capture-14.png').convert('RGB')
img=Image.new('RGB',(1200,800),'#f3f5f8');d=ImageDraw.Draw(img)
for x,source in [(70,before),(670,after)]:
 img.paste(source,(x,190));zoom=source.crop((284,184,300,200)).resize((192,192),Image.Resampling.NEAREST);img.paste(zoom,(x+80,450))
 d.rectangle((x-1,189,x+300,390),outline='#7b8794',width=1)
 d.rectangle((x+79,449,x+272,642),outline='#7b8794',width=1)
 d.rectangle((x,690,x+400,715),fill='#dfe5ec');
d.rectangle((70,690,150,715),fill='#d7263d')
img.save(r/'accept/d-before-after-base.png')
shapes=[{'kind':'text','at':[40,55],'text':'Region capture: remove the selector cursor before the frame fence','fontPixels':26,'color':'#172b4d'},
 {'kind':'text','at':[70,125],'text':'BEFORE nightly 7fc609dc4','fontPixels':24,'color':'#d7263d'},
 {'kind':'text','at':[670,125],'text':'AFTER b88e817a1','fontPixels':24,'color':'#047857'},
 {'kind':'text','at':[70,165],'text':'Actual 300 x 200 captured image','fontPixels':18,'color':'#172b4d'},
 {'kind':'text','at':[670,165],'text':'Actual 300 x 200 captured image','fontPixels':18,'color':'#172b4d'},
 {'kind':'text','at':[70,415],'text':'Last 16 x 16 pixels, enlarged 12x (nearest)','fontPixels':17,'color':'#172b4d'},
 {'kind':'text','at':[670,415],'text':'Same corner and enlargement','fontPixels':17,'color':'#172b4d'},
 {'kind':'arrow','from':[460,530],'to':[332,631],'width':4,'color':'#d7263d'},
 {'kind':'text','at':[365,500],'text':'11 x 11 cursor fragment','fontPixels':19,'color':'#d7263d'},
 {'kind':'text','at':[70,666],'text':'6 / 30 captures contain cursor pixels','fontPixels':20,'color':'#d7263d'},
 {'kind':'text','at':[670,666],'text':'0 / 30; every pixel matches the reference','fontPixels':20,'color':'#047857'},
 {'kind':'text','at':[40,765],'text':'Fresh d69 KVM guests | Omarchy 4.5 / Hyprland 0.56.2 | software renderer | two monitors','fontPixels':18,'color':'#172b4d'}]
(r/'accept/d-annotations.json').write_text(json.dumps(shapes))
