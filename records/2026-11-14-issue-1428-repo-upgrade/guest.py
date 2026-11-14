import subprocess,sys,shlex
prefix='ssh -i ~/work/put.gd/work/lab-bootstrap-omarchy/identity -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=~/work/put.gd/work/lab-images/omarchy-hyprland-20261108/known_hosts -p 22440 lab@127.0.0.1 '
sys.exit(subprocess.call([sys.executable,'work/repo1428/run.py','d69',sys.argv[1],prefix+shlex.quote(sys.argv[2])]))
