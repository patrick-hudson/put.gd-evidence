import sys,shlex
from vm_remote import remote
r=sys.argv[1];case=sys.argv[2]
remote('python3 ~/work/svm1398/vm_cmd.py '+r+' '+shlex.quote('python3 ~/putgd-lab/guest_campaign.py '+case))
