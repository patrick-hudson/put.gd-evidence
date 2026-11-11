import sys,concurrent.futures,json
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');p=next((base/'v2artifacts/release-appimage').glob('*.AppImage'))
def go(k):
 r=base/'repo/work/lab-runs'/(k+'f')
 try:
  x=lab.install(r,appimage=p);(base/(k+'-v2install.json')).write_text(json.dumps(x,indent=2));print(k,'installed',flush=True)
  print(k,lab.guest_session(r,'python3 /home/lab/v2guest.py init',timeout=180),flush=True)
 except Exception as e:print(k,'ERROR',e,flush=True)
with concurrent.futures.ThreadPoolExecutor(4) as pool:list(pool.map(go,'obnk'))
