import accept as A,trial_relative as T,subprocess,time,json
import rfb
P=A.P;L=A.L;T.os.environ.update(A.E)
def at():return {k:int(v) for k,v in (x.split('=',1) for x in subprocess.check_output(['xdotool','getmouselocation','--shell'],env=A.E,text=True).splitlines())}
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox')
 mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');T.flat();time.sleep(.5)
 v=rfb.RFB(5900);v.pointer(500,400);v.close();time.sleep(.3);a=at()
 for _ in range(20):mouse.stdin.write('m 5 0\n');mouse.stdin.flush();time.sleep(.01)
 time.sleep(.1);b=at()
 for _ in range(20):mouse.stdin.write('m 0 5\n');mouse.stdin.flush();time.sleep(.01)
 time.sleep(.1);c=at();r={'before':a,'after100x':b,'after100y':c,'profile':T.x11_profile(),'properties':subprocess.check_output(['xinput','list-props','putgd-lab relative mouse with wheel'],text=True,env=A.E)}
 (P/'relative-calibration.json').write_text(json.dumps(r,indent=1));print(json.dumps(r),flush=True);assert [b['X']-a['X'],b['Y']-a['Y'],c['X']-b['X'],c['Y']-b['Y']]==[100,0,0,100]
finally:
 if 'mouse'in globals():mouse.stdin.write('q\n');mouse.stdin.flush();mouse.wait(5)
 L.browser_stop()
