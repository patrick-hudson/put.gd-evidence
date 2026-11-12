from pathlib import Path
import sys
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
r=Path('/home/patrick/work/put.gd/work/lab-runs/s3h')
print(lab.ssh(r,'tail -c 1500 /home/lab/work/s3a/browsercases.py.console; sudo -n /usr/bin/pacman -S --noconfirm --needed firefox > /home/lab/accept3-firefox-install.log 2>&1; code=$?; tail -c 2000 /home/lab/accept3-firefox-install.log; exit $code',timeout=400),flush=True)
