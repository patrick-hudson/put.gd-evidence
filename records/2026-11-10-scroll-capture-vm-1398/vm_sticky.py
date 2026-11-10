import sys,shlex
from vm_remote import remote
r=sys.argv[1]
cmd='python3 ~/putgd-lab/scroll_run_vm.py --out /home/lab/putgd-lab/sticky --package /home/lab/ci.AppImage --rect 0,0,1280,800 --rows 60 --format fixture --code-width 1280 --header 40 --footer 40 --max-height 5000 --png-root /home/lab/putgd-lab/archive --png-root /home/lab/putgd-lab/data > ~/putgd-lab/sticky-console.log 2>&1 || true; cat ~/putgd-lab/sticky-console.log'
remote('python3 ~/work/svm1398/vm_cmd.py '+r+' '+shlex.quote(cmd))
