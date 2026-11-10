import sys,shlex
from vm_remote import remote
r=sys.argv[1];case=sys.argv[2];rect=sys.argv[3] if len(sys.argv)>3 else '0,100,1200,600'
cmd=f'python3 ~/putgd-lab/scroll_run_vm.py --out /home/lab/putgd-lab/{case} --package /home/lab/ci.AppImage --rect {rect} --rows 60 --format fixture --max-height 2000 --height 2000 --expect-end height_cap --code-width 1280 --png-root /home/lab/putgd-lab/archive --png-root /home/lab/putgd-lab/data > ~/putgd-lab/{case}-console.log 2>&1 || true; cat ~/putgd-lab/{case}-console.log'
remote('python3 ~/work/svm1398/vm_cmd.py '+r+' '+shlex.quote(cmd))
