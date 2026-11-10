import sys,json,time
from pathlib import Path
exec(compile(Path('/tmp/p1363-checks.py').read_text().split('build = cli(')[0],'/tmp/p1363-checks.py','exec'))
E=Path(ROOT)/'work/acceptance-1363'/run
mode=sys.argv[4]
def save(n,x):(E/(n+'.json')).write_text(json.dumps(x,indent=2))
if mode=='right':
 guest(ENV+'python3 /tmp/wayland_pointer.py click %s %s --button right --extent 2304 800'%tuple(sys.argv[5:7]));time.sleep(.6);dump(1).save(E/(sys.argv[7]+'.png'))
elif mode=='wheel':
 guest(ENV+'python3 /tmp/wayland_pointer.py wheel %s %s %s --extent 2304 800'%tuple(sys.argv[5:8]));time.sleep(.7);dump(1).save(E/(sys.argv[8]+'.png'))
elif mode=='immediate':
 before={o['id'] for o in cli('operation.recent')['operations']};began=time.monotonic();lab('key','--run',RUN,'ctrl','shift','1');time.sleep(.5);dump(1).save(E/'immediate-shortcut-selector.png');drag(300,300,600,500);released=time.monotonic();ops=[o for o in cli('operation.recent')['operations'] if o['id'] not in before];assert len(ops)==1,ops
 r=wait(ops[0]['id']);r['afterRelease']=time.monotonic()-released;save('immediate-shortcut',r);im=fetch(r['path']);im.save(E/'immediate-shortcut.png');assert im.size==(300,200) and r['afterRelease']<2.8,r
 move(700,600);before={o['id'] for o in cli('operation.recent')['operations']};lab('key','--run',RUN,'ctrl','alt','r');time.sleep(.4);ops=[o for o in cli('operation.recent')['operations'] if o['id'] not in before];r=wait(ops[0]['id']);save('real-key-repeat',r);rep=fetch(r['path']);rep.save(E/'real-key-repeat.png');assert ImageChops.difference(im,rep).getbbox() is None
 print('PASS immediate region with GUI delay; repeat identical')
elif mode=='omission':
 name=sys.argv[5];shown=Image.open(E/(name+'-countdown.png')).convert('RGB');clean=Image.open(E/(name+'-after.png')).convert('RGB');cap=Image.open(E/(name+'-image.png')).convert('RGB');box=(400,10,625,80);a=differs(clean.crop(box),cap.crop(box));b=differs(shown.crop(box),cap.crop(box));save(name+'-omission',dict(clean=a,countdown=b,passed=a<2 and b>8));print(a,b);assert a<2 and b>8
