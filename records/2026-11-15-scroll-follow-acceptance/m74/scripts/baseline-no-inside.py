import accept as A,json,time,subprocess
import rfb
P=A.P;L=A.L;sid=None
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 sid=A.rpc('scroll.prepare',{'rect':[0,0,1920,1080]})['id'];A.rpc('scroll.start',{'id':sid});time.sleep(2)
 v=rfb.RFB(5900);v.screenshot(P/'full-region-baseline.png');v.close()
 pids=subprocess.run(['pgrep','-x','putgd-record'],capture_output=True,text=True).stdout.split();windows=[]
 for pid in pids:
  ids=subprocess.run(['xdotool','search','--onlyvisible','--pid',pid],env=A.E,capture_output=True,text=True).stdout.split()
  for wid in ids:windows.append({'pid':pid,'id':wid,'xwininfo':subprocess.run(['xwininfo','-id',wid],env=A.E,capture_output=True,text=True).stdout})
 result={'beforeStop':A.rpc('scroll.inspect',{'id':sid}),'visibleHelperWindows':windows,'stop':A.rpc('scroll.stop',{'id':sid}),'note':'Published nightly has the earlier Stop bar and no inside-corner placement feature. This records the actual full-region behavior; it is not a direct test of the new user-driver or inside buttons.'};(P/'full-region-baseline.json').write_text(json.dumps(result,indent=1));print(json.dumps(result),flush=True)
finally:
 if sid:
  try:
   if A.rpc('scroll.inspect',{'id':sid}).get('state')=='capturing':A.rpc('scroll.cancel',{'id':sid})
  except Exception:pass
 L.browser_stop()
