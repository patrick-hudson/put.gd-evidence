from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
r=Path('/home/patrick/work/pg-cd/work/lab-runs/bc7');out=r/'accept'
rows=json.loads((out/'loaded-results.json').read_text());metrics=json.loads((out/'load-metrics.json').read_text())
assert len(rows)==10 and all(x['operation']['state']=='completed' for x in rows)
blank=json.loads((out/'blanked-unlocked.json').read_text());assert blank['operation']['error']['code']=='session_locked' and not blank['operation']['items']
files=json.loads((out/'blank-files.json').read_text());assert files['before']==files['after']
img=Image.new('RGB',(1280,900),'#f3f5f8');d=ImageDraw.Draw(img)
shot=Image.open(out/'loaded-4.png').convert('RGB').resize((512,320));img.paste(shot,(40,150))
d.rectangle((600,150,1240,530),fill='#172b4d');d.rectangle((40,610,600,795),fill='#172b4d');d.rectangle((650,610,1240,795),fill='#172b4d')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',18)
lines=['Loaded capture    State        Elapsed ms']+[f'{i+1:2}                completed       {row["milliseconds"]:4}' for i,row in enumerate(rows)]
for i,line in enumerate(lines):d.text((617,163+i*31),line,font=font,fill='white')
for i in range(3):
 row=json.loads((out/f'locked-{i}.json').read_text());assert row['operation']['error']['code']=='session_locked'
 d.text((55,635+i*45),f'gtklock {i+1}: session_locked ({row["milliseconds"]} ms)',font=font,fill='white')
for i,line in enumerate(['Virtual-1 off; LockedHint=no','gtklock-absent','capture: session_locked; no files','power restored: capture completed']):d.text((667,628+i*39),line,font=font,fill='white')
img.save(out/'stress-report-base.png')
shapes=[{'kind':'text','at':[40,55],'text':'Three-second frame witness: busy, blanked and locked','fontPixels':28,'color':'#172b4d'},
 {'kind':'text','at':[40,119],'text':'Actual captured Firefox canvas (local synthetic page)','fontPixels':19,'color':'#172b4d'},
 {'kind':'text','at':[40,493],'text':'10 / 10 consecutive requests completed','fontPixels':23,'color':'#047857'},
 {'kind':'text','at':[40,538],'text':f'Two-vCPU guest: {metrics["guestBusyPercent"]}% busy during the run','fontPixels':20,'color':'#172b4d'},
 {'kind':'text','at':[40,579],'text':'Real gtklock: 3 / 3 refusals, no output files','fontPixels':22,'color':'#047857'},
 {'kind':'text','at':[650,579],'text':'Blanked, not locked: also refused','fontPixels':22,'color':'#172b4d'},
 {'kind':'arrow','from':[585,815],'to':[354,742],'width':4,'color':'#d7263d'},
 {'kind':'text','at':[40,828],'text':'Head 2354d9f69 / CI merge 2562221fa329 | setup 5s + frame 3s = 8s maximum','fontPixels':20,'color':'#172b4d'},
 {'kind':'text','at':[40,865],'text':'Elapsed times include IPC/polling; screenshots and operations are from the exact CI AppImage.','fontPixels':17,'color':'#172b4d'}]
(out/'stress-report-annotations.json').write_text(json.dumps(shapes))
