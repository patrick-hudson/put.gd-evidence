import accept as A,subprocess,importlib.util,time,rfb,json
for n in ['putgd-record','firefox','chrome']:assert not subprocess.run(['pgrep','-x',n],capture_output=True,text=True).stdout.strip(),n
spec=importlib.util.spec_from_file_location('rc',A.P/'relative-control-native.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
u=subprocess.Popen(['sudo','-n','python3',str(A.P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert u.stdout.readline().startswith('ready')
try:
 import trial_relative as T;T.os.environ.update(A.E);T.flat();C=m.Control(A,u);C.anchor_before_prepare(100,300);C.move(1869,859);print('native pointer before closing own incomplete notice',C.origin(),flush=True);C.click();C.move(100,300);time.sleep(1)
finally:u.stdin.write('q\n');u.stdin.flush();u.wait(5)
v=rfb.RFB(5900);v.screenshot(A.P/'own-notice-dismissed.png');v.close()
with(A.P/'chromium-news-user-notice-dismissed.log').open('w')as f:r=subprocess.run(['python3','-u','pages-relative.py','chromium','news','user'],env=dict(A.os.environ,LAB_TAG='notice-dismissed'),stdout=f,stderr=subprocess.STDOUT)
print('article retry exit',r.returncode,flush=True);raise SystemExit(r.returncode)

