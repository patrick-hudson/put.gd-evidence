from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
r=Path('/var/home/patrick/a1364'); out=r/'evidence';out.mkdir(exist_ok=True)
try:f=ImageFont.truetype('DejaVuSans.ttf',18);small=ImageFont.truetype('DejaVuSans.ttf',14)
except OSError:f=small=ImageFont.load_default()
head='Aurora · Plasma / KWin 6.8.2 · Wayland · put.gd 26.1110.4538'
# Crop to the product's bar and call out its actual toggle and meter.
c=Image.new('RGB',(1000,350),'#20242b');d=ImageDraw.Draw(c);d.text((14,10),head,font=f,fill='white')
for i,(key,title) in enumerate([('plugged','Microphone offered, off'),('on','Microphone on, live meter'),('none','No microphone')]):
 im=Image.open(r/f'runs/e/frames/pr-mp4-1-ready-{key}.png').convert('RGB').crop((0,548,970,604));y=70+i*90
 c.paste(im,(10,y));d.text((14,y-26),title,font=f,fill='#6ee7b7');d.rectangle((375,y+8,540,y+48),outline='#fb7185',width=3)
c.save(out/'bar-plasma.png')
im=Image.open(r/'runs/g-monitor/frames/pr-mp4-1-export-click.png').convert('RGB').crop((130,10,340,125)).resize((630,345))
c=Image.new('RGB',(850,450),'#20242b');c.paste(im,(15,80));d=ImageDraw.Draw(c);d.text((15,12),head,font=small,fill='white');d.text((15,42),'KWin draws the click ring into the monitor clip',font=f,fill='white');d.rectangle((190,192,260,266),outline='#6ee7b7',width=3);d.line((650,230,260,230),fill='#6ee7b7',width=3);d.text((660,215),'Click ring',font=f,fill='#6ee7b7');d.text((15,430),'Left click: +33 ms; ring + label centre 43.9 px from click (Plasma allowance 48 px).',font=small,fill='white');c.save(out/'ring-plasma.png')
im=Image.open(r/'support-preview2.png').convert('RGB').crop((300,77,1620,958));c=Image.new('RGB',(1320,951),'#20242b');c.paste(im,(0,70));d=ImageDraw.Draw(c);d.text((16,10),head,font=f,fill='white');d.text((16,38),'Desktop support details: KWin effect available; window-stream limitation explained',font=f,fill='#6ee7b7');d.rectangle((252,714,1001,779),outline='#fb7185',width=3);c.save(out/'support-plasma.png')
# Alignment chart: primary exported clips, targets and acceptance bound.
import json
items=[]
for name in ['a','b','b-repeat','nightly']:
 for i,z in enumerate(json.loads((r/f'runs/{name}/results.json').read_text())['rounds']):
  v=z.get('clips',{}).get('export',{}).get('medianMs')
  if v is not None:items.append((f'{name} {z["format"]} #{i+1}',v))
c=Image.new('RGB',(1000,100+34*len(items)),'white');d=ImageDraw.Draw(c);d.text((12,10),'Audio minus picture, exported clip medians (ms)',font=f,fill='black')
x=lambda t:350+(t+50)*3
for t in [-45,-33,0,33,125]:
 d.line((x(t),50,x(t),c.height-10),fill='#cccccc',width=1);d.text((x(t)-12,32),str(t),font=small,fill='black')
for i,(label,v) in enumerate(items):
 y=70+34*i;d.text((12,y-9),label,font=small,fill='black');d.ellipse((x(v)-5,y-5,x(v)+5,y+5),fill='#059669' if abs(v)<=33 else '#d97706');d.text((x(v)+10,y-9),f'{v:+g}',font=small,fill='black')
c.save(out/'alignment-plasma.png')
print('pictures created')
