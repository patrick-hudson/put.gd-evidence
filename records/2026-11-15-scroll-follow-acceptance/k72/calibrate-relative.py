import accept as A,trial_relative as T,subprocess,time,json
import rfb
P=A.P;L=A.L;T.os.environ.update(A.E)
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect()
 b.js('document.documentElement.setAttribute("data-sfa-pointer","[]");document.addEventListener("mousemove",e=>document.documentElement.setAttribute("data-sfa-pointer",JSON.stringify([e.screenX,e.screenY])));return 0;')
 mouse=subprocess.Popen(([] if A.os.access('/dev/uinput',A.os.W_OK) else ['sudo','-n'])+['python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');T.flat();time.sleep(.5)
 v=rfb.RFB(5900);v.pointer(499,400);time.sleep(.1);v.pointer(500,400);v.close();time.sleep(.3)
 def at():return json.loads(b.js('return document.documentElement.getAttribute("data-sfa-pointer")'))
 a=at()
 for _ in range(20):mouse.stdin.write('m 5 0\n');mouse.stdin.flush();time.sleep(.01)
 time.sleep(.15);c=at()
 for _ in range(20):mouse.stdin.write('m 0 5\n');mouse.stdin.flush();time.sleep(.01)
 time.sleep(.15);d=at();r={'before':a,'after100x':c,'after100y':d,'desktop':A.DESKTOP,'method':'Own browser mousemove event screenX/screenY, before any product capture. Native configured flat profile, relative uinput motion.'};(P/'relative-calibration.json').write_text(json.dumps(r,indent=1));print(json.dumps(r),flush=True);assert [c[0]-a[0],c[1]-a[1],d[0]-c[0],d[1]-c[1]]==[100,0,0,100]
finally:
 if 'mouse'in globals():mouse.stdin.write('q\n');mouse.stdin.flush();mouse.wait(5)
 L.browser_stop()
