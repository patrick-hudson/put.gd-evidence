import sys,time,json,shlex
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');k=sys.argv[1];r=base/'repo/work/lab-runs'/(k+'f');o=base/'v2evidence'/k
s=(base/'v2ruler-notice.py');s.write_text(Path('/home/patrick/work/sf1398/qt_fixture.py').read_text().replace('w.showFullScreen()','w.showMaximized()'))
lab.put(r,s,'/home/lab/v2ruler-notice.py')
def cmd(c):return lab.guest_session(r,c,timeout=300)
print(cmd('python3 /home/lab/v2guest.py patch '+shlex.quote(json.dumps({'preferences':{'scrollCaptureMaxHeight':2000},'actions':{'scroll':{'destination':'local'}}}))),flush=True)
pid=int(cmd('nohup python3 /home/lab/v2ruler-notice.py > /tmp/v2/notice-fixture.log 2>&1 < /dev/null & echo $!').strip());time.sleep(4)
im=Image.open(lab.screenshot(r,'v2-notice-ready')['path']).convert('RGB');im.save(o/'notice-ready.png');ys=[]
for y in range(50,200):
 if all(sum(im.getpixel((100+64+c*55+27,y)))<200 for c in range(16)) and all(sum(im.getpixel((100+64+c*55+27,y+1)))<200 for c in range(16)):ys.append(y)
assert ys, 'cannot locate full first ruler line'
y=min(ys);rect='100,%d,960,600'%y
print('resolved',rect,flush=True)
print(cmd('python3 /home/lab/v2guest.py case cap-notify '+rect),flush=True);time.sleep(.5)
Image.open(lab.screenshot(r,'v2-notice-visible')['path']).save(o/'height-cap-notification.png')
print(cmd('kill '+str(pid)),flush=True)
