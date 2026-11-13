import os
from pathlib import Path
p=Path('/home/lab/b1428/measure')
os.environ.update(PUTGD_CONFIRM_FIXTURE='/home/lab/b1428/confirm-ai.txt',PUTGD_MEASUREMENT_SOURCE='/home/lab/b1428/r',PUTGD_MEASUREMENT_VNC_PORT='5997')
args=['python3',str(p/'text_proof.py'),'--desktop','ubuntu-wayland-appimage-8a','--leader','gsd-power','gnome-shell','--app','/home/lab/b1428/candidate.AppImage','--cli','/home/lab/b1428/cli','--input-socket','/home/lab/b1428-input.sock','--screen','1920','1080','--region','600','430','1400','650','--triggers','hotkey','--fixture','python3',str(p/'fixture.py'),'--expect','ALPHA BRAVO CHARLIE\nSYNTHETIC TEXT 1428\nhello@example.test','--first-light','--helper-watch',str(p/'helper_watch.py'),'--rfb','none','--settle','20']
os.execvp(args[0],args)
