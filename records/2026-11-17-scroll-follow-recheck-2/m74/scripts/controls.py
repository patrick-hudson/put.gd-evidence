import accept as A,trial_relative as T,time,json,subprocess,re,os,sys,io,contextlib
from pathlib import Path
import rfb
P=A.P;L=A.L;os.environ.update(A.E)
T.cli=lambda path,m,p:{'ok':True,'result':A.rpc(m,p)}
profile=P/'profile-firefox'
if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
try:
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 if sys.argv[1]=='inside':
  mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready');T.flat();rows=[]
  try:
   for button in ['autoScroll','done','cancel']:
    b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(.5);v=rfb.RFB(5900);v.pointer(960,540);v.close()
    offset=(P/'helper.log').stat().st_size;sid=A.rpc('scroll.prepare',{'rect':[0,0,1920,1080]})['id'];A.rpc('scroll.start',{'id':sid});time.sleep(1)
    text=(P/'helper.log').read_text();m=list(re.finditer(r'scroll: bar at .*'+button+r' (-?\d+),(-?\d+) (\d+)x(\d+)',text))[-1];x,y,w,h=map(int,m.groups());old,actual,wid=T.x11_bar(text);x+=actual[0]-old[0];y+=actual[1]-old[1];target=[x+w//2,y+h//2]
    loc=dict(z.split('=',1)for z in subprocess.check_output(['xdotool','getmouselocation','--shell'],env=A.E,text=True).splitlines());sx,sy=int(loc['X']),int(loc['Y']);steps=max(1,int(((target[0]-sx)**2+(target[1]-sy)**2)**.5/6))
    for i in range(1,steps+1):
     dx=round((target[0]-sx)*i/steps)-round((target[0]-sx)*(i-1)/steps);dy=round((target[1]-sy)*i/steps)-round((target[1]-sy)*(i-1)/steps);mouse.stdin.write(f'm {dx} {dy}\n');mouse.stdin.flush();time.sleep(.01)
    time.sleep(.1);before=A.rpc('scroll.inspect',{'id':sid});mouse.stdin.write('d\n');mouse.stdin.flush();time.sleep(.06);mouse.stdin.write('u\n');mouse.stdin.flush();time.sleep(1);after=A.rpc('scroll.inspect',{'id':sid})
    final=after
    if button=='autoScroll':worked=after.get('driver')=='putgd';final=A.rpc('scroll.stop',{'id':sid})
    else:worked=after.get('state')==('done'if button=='done'else'cancelled')
    if after.get('state')=='capturing'and button!='autoScroll':A.rpc('scroll.cancel',{'id':sid})
    row={'button':button,'target':target,'firstClickWorked':worked,'before':before,'after':after,'capture':final};rows.append(row);(P/'inside-results.json').write_text(json.dumps(rows,indent=1));(P/('inside-'+button+'.log')).write_bytes((P/'helper.log').read_bytes()[offset:]);print(json.dumps(row),flush=True)
  finally:mouse.stdin.write('q\n');mouse.stdin.flush();mouse.wait(5)
 else:
  sid=A.rpc('scroll.prepare',{'rect':[240,200,1440,820]})['id'];A.rpc('scroll.start',{'id':sid});time.sleep(1);A.rpc('scroll.cancel',{'id':sid})
  for i in range(5):
   b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(1)
   m=list(re.finditer(r'scroll: bar at .*done (-?\d+),(-?\d+) (\d+)x(\d+)',(P/'helper.log').read_text()))[-1];x,y,w,h=map(int,m.groups());stop=f'{x+w//2},{y+h//2}'
   sys.argv=['trial','--cli',str(P/'cli'),'--rect','240,200,1440,820','--stop',stop,'--log',str(P/'helper.log'),'--rel','--label',f'random-{i+1}','--start','1','--jitter','5','--speed','600']
   buf=io.StringIO()
   with contextlib.redirect_stdout(buf):T.main()
   text=buf.getvalue();print(text,flush=True)
   row=json.loads([line for line in text.splitlines()if line.startswith('{')][-1]);row['capture']=A.rpc('scroll.inspect',{'id':row['id']});(P/('pause-random-'+str(i+1)+'.json')).write_text(json.dumps(row,indent=1))
finally:L.browser_stop()
