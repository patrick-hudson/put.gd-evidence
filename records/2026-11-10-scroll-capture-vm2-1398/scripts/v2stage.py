exec(open('/home/patrick/work/svm1398/v2ctl.py').read().split("if sys.argv[1]=='deps':")[0])
for k in 'obnk':
 r=root/(k+'f')
 for n in ['v2guest.py','v2text.py','v2receiver.py']:lab.put(r,Path('/home/patrick/work/svm1398')/n,'/home/lab/'+n)
 lab.put(r,Path('/home/patrick/work/sf1398/verify_text.py'),'/home/lab/verify_text.py')
 lab.put(r,Path('/home/patrick/work/sf1398/qt_fixture.py'),'/home/lab/v2ruler.py')
 lab.put(r,Path('/home/patrick/work/svm1398/ruler-vm.html'),'/home/lab/v2ruler.html')
 import shlex
 try:print(k,lab.guest_session(r,'python3 -c '+shlex.quote('import gi; gi.require_version("Gtk","4.0"); from gi.repository import Gtk; import PyQt6; import PIL; import numpy; print("dependencies-ready")')),flush=True)
 except Exception as e:print(k,str(e),flush=True)
