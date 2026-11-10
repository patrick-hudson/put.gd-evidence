import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
name=sys.argv[1];r=Path('/home/patrick/work/pg-cd/work/lab-runs')/name;o=r/'accept'
before=Path('/tmp/pg-d-final-before')
baseline=json.loads((before/'summary.json').read_text());assert baseline['n']==20 and baseline['affected']==8
final=o/'D-final-immediate20';summary=json.loads((final/'summary.json').read_text());assert summary['n']==20 and summary['affected']==0 and summary['otherDifferences']==0
extra=json.loads((o/'D-final-delayed-repeat/summary.json').read_text());assert all(v['n']==10 and v['affected']==0 for v in extra.values())
version=json.loads((final/'version.json').read_text());assert version['gitCommit']=='ccf0ebb728a31a92c0fa30fd305aa6864f6cb0fc'
img=Image.new('RGB',(1200,900),'#f3f5f8');draw=ImageDraw.Draw(img)
for x,p in [(70,before/'capture.png'),(670,final/'capture-0.png')]:
 source=Image.open(p).convert('RGB');assert source.size==(300,200)
 img.paste(source,(x,190));img.paste(source.crop((284,184,300,200)).resize((192,192),Image.Resampling.NEAREST),(x+80,450))
 draw.rectangle((x-1,189,x+300,390),outline='#7b8794',width=1)
 draw.rectangle((x+79,449,x+272,642),outline='#7b8794',width=1)
 draw.rectangle((x,690,x+400,715),fill='#dfe5ec')
draw.rectangle((70,690,230,715),fill='#d7263d');img.save(o/'d-final-before-after-base.png')
shapes=[
 {'kind':'text','at':[40,55],'text':'Blank the selector cursor before the frame fence','fontPixels':28,'color':'#172b4d'},
 {'kind':'text','at':[70,122],'text':'BEFORE capture 13570fca9 / CI4498','fontPixels':22,'color':'#d7263d'},
 {'kind':'text','at':[670,122],'text':'AFTER ccf0ebb728 / CI4515','fontPixels':22,'color':'#047857'},
 {'kind':'text','at':[70,165],'text':'Actual 300 x 200 capture','fontPixels':19,'color':'#172b4d'},
 {'kind':'text','at':[670,165],'text':'Actual 300 x 200 capture','fontPixels':19,'color':'#172b4d'},
 {'kind':'text','at':[70,415],'text':'Last 16 x 16 pixels, enlarged 12x (nearest)','fontPixels':17,'color':'#172b4d'},
 {'kind':'text','at':[670,415],'text':'Same corner and enlargement','fontPixels':17,'color':'#172b4d'},
 {'kind':'arrow','from':[460,530],'to':[332,631],'width':4,'color':'#d7263d'},
 {'kind':'text','at':[365,500],'text':'59 cursor pixels','fontPixels':19,'color':'#d7263d'},
 {'kind':'text','at':[70,666],'text':'8 / 20 immediate drags leak the cross','fontPixels':20,'color':'#d7263d'},
 {'kind':'text','at':[670,666],'text':'0 / 20 immediate drags; all pixels exact','fontPixels':20,'color':'#047857'},
 {'kind':'text','at':[670,759],'text':'Delayed region: 10 / 10 exact','fontPixels':20,'color':'#047857'},
 {'kind':'text','at':[670,793],'text':'Immediate repeat: 10 / 10 exact','fontPixels':20,'color':'#047857'},
 {'kind':'text','at':[40,850],'text':'Fresh two-head KVM guests | Omarchy 4.5 / Hyprland 0.56.2 | software rendering','fontPixels':18,'color':'#172b4d'}]
(o/'d-final-annotations.json').write_text(json.dumps(shapes,indent=2))
