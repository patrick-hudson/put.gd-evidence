import sys,json
from pathlib import Path
sys.argv=['checks','ah7','/home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity','hyprland']
exec(compile(Path('/tmp/p1363-ah7/checks.py').read_text().split('build = cli(')[0],'<checks>','exec'))
p=Path('/tmp/p1363-checks-genh0wos');a=Image.open(p/'legacy-reference.png').convert('RGB');b=Image.open(p/'legacy-during.png').convert('RGB')
desktop='kde' # Exercise just the image locator fallback on real retained frames, not desktop acceptance.
box=countdown_box(a,b,1,'regression-wallpaper');assert 402 <= box[0] <= 404 and 621 <= box[2] <= 623 and box[1::2]==(42,66) and ((box[0]+box[2])//2,(box[1]+box[3])//2)==(512,54),box;print('wallpaper-contaminated frame: actual pill',box,flush=True)
try:countdown_box(a,a,1,'regression-no-pill')
except RuntimeError:print('no visible pill: rejected loudly',flush=True)
else:raise AssertionError('No-pill frame accepted')
print('REGRESSION_FRAMES',WORK,flush=True)
