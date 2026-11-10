import sys,os,stat,re,time,json
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
name,desktop=sys.argv[1:];assert re.fullmatch(r'(hc|bc)[0-9]+',name)
r=Path('/home/patrick/work/pg-cd/work/lab-runs')/name;lab.verify_owned_guest(r)
o=r/'accept';request=o/'unlock-request.json';permit=r/'unlock-authorized.json';verified=r/'unlock-verified.json'
for p in (permit,verified):assert not p.exists()
if desktop=='hyprland':lab.key(r,['esc']);time.sleep(.5)
for h in (0,1):Image.open(lab.screenshot(r,'unlock-request',h)['path']).save(o/f'unlock-request-head{h}.png')
request.write_text(json.dumps({'run':name,'desktop':desktop,'status':'awaiting-agent-visual-check-of-focused-masked-field'}));print('Awaiting masked-field visual verification for '+name,flush=True)
def await_marker(path):
 end=time.monotonic()+180
 while not path.exists():
  if time.monotonic()>end:raise RuntimeError('Visual verification not supplied; no login input sent')
  time.sleep(.1)
 info=path.lstat();assert stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)==0o600
await_marker(permit)
text=Path('/home/patrick/work/pg-cd/docs/lab/vm-lab/hosts-and-bases.md').read_text();m=re.search(r'approved `lab` / `([^`]+)` default',text);assert m
p=r/'unlock-input';fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.write(fd,m.group(1).encode());os.close(fd)
try:
 info=p.lstat();assert stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)==0o600
 value=p.read_text();assert value
 for c in value:lab.key(r,['minus' if c=='-' else c])
 lab.key(r,['ret'])
finally:p.unlink()
time.sleep(1)
for h in (0,1):Image.open(lab.screenshot(r,'unlock-after',h)['path']).save(o/f'unlock-after-head{h}.png')
request.write_text(json.dumps({'run':name,'desktop':desktop,'status':'awaiting-agent-visual-check-of-unlocked-desktop'}));print('Input removed; awaiting unlocked-desktop visual verification',flush=True)
await_marker(verified)
print('Unlocked desktop verified; returning to unchanged capture checks',flush=True)
