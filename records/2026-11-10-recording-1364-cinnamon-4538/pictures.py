from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
r=Path('/tmp/c1364'); out=r/'pictures';out.mkdir(exist_ok=True)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
b=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
for state,label,box in [('on','Microphone on: simulated input and live meter',(370,8,530,44)),('none','No microphone: monitor inputs are excluded',(365,8,515,44))]:
 im=Image.open(r/'f/frames'/('pr-mp4-1-ready-'+state+'.png')).convert('RGB').crop((0,550,946,602))
 canvas=Image.new('RGB',(974,158),(30,30,34));canvas.paste(im,(14,52));d=ImageDraw.Draw(canvas)
 d.text((14,12),label,font=b,fill='white');x0,y0,x1,y1=box;d.rectangle((x0+14,y0+52,x1+14,y1+52),outline=(255,64,129),width=3)
 d.text((14,116),'m74 / Cinnamon 6.6.9 X11 / put.gd 26.1110.4538 / PR cccf91a50',font=f,fill='white')
 canvas.save(out/('microphone-'+state+'.png'))
frame=Image.open(r/'h-monitor-on/frames/pr-mp4-1-export-click.png').convert('RGB')
# Crop only the lab cover around the first ring, then enlarge for legibility.
im=frame.crop((140,7,260,127)).resize((360,360))
canvas=Image.new('RGB',(800,430),(30,30,34));canvas.paste(im,(14,52));d=ImageDraw.Draw(canvas)
d.text((14,12),'Click ring in exported monitor recording',font=b,fill='white')
d.rectangle((120,160,265,305),outline=(255,64,129),width=3)
d.text((395,100),'XInput2: 3 / 3 rings',font=b,fill='white');d.text((395,140),'First ring: 0 ms, dx -1 / dy -1.3 px',font=f,fill='white')
d.text((395,185),'Box marks the click ring.',font=f,fill='white');d.text((395,230),'m74 Cinnamon 6.6.9 X11',font=f,fill='white')
d.text((395,270),'put.gd 26.1110.4538',font=f,fill='white');d.text((395,310),'PR head cccf91a50',font=f,fill='white')
canvas.save(out/'click-ring.png')
# Alignment chart: exported audio-minus-picture run medians.
rows=[]
for case in ('a','b'):
 report=json.loads((r/case/'results.json').read_text())
 for entry in report['rounds']: rows.append((case+' '+entry['format'],entry['clips']['export']['medianMs']))
canvas=Image.new('RGB',(900,380),(30,30,34));d=ImageDraw.Draw(canvas)
d.text((20,15),'Audio relative to visual marker (ms)',font=b,fill='white')
def x(v):return 270+(v+50)*3
for v in (-45,-33,0,33,125):
 d.line((x(v),65,x(v),300),fill=(80,170,110) if v in (-45,125) else (120,120,130),width=2)
 d.text((x(v)-15,310),str(v),font=f,fill='white')
for idx,(label,value) in enumerate(rows):
 y=95+idx*52;d.text((20,y-10),label,font=f,fill='white');d.ellipse((x(value)-6,y-6,x(value)+6,y+6),fill=(255,64,129));d.text((x(value)+12,y-10),str(value),font=f,fill='white')
d.text((20,350),'m74 Cinnamon/X11; build 4538. Green limits: acceptance. Grey: one-frame target.',font=f,fill='white')
canvas.save(out/'alignment.png')
