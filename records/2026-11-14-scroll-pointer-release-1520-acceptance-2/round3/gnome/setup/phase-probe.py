from pathlib import Path
from trial import cli,flat
import subprocess,time,json,re,random
l=Path.home()/'work/s5302';a=l/'a';c=str(l/'bin/cli-a');log=a/'helper.log'
for n in range(10):
 subprocess.run(['firefox','--profile',str(l/'ff'),'https://en.wikipedia.org/wiki/Linux']);time.sleep(5)
 m=subprocess.Popen(['sudo','-n','python3',str(l/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert m.stdout.readline().startswith('ready');flat();off=log.stat().st_size;s=cli(c,'scroll.prepare',{'rect':[470,200,980,720]})['result']['id'];cli(c,'scroll.start',{'id':s});delay=random.uniform(1,6);time.sleep(delay);p=log.stat().st_size;deadline=time.monotonic()+5
 while time.monotonic()<deadline:
  b=log.read_bytes();chunk=b[p:];p=len(b)
  if re.search(rb'pointer 16,744 sent',chunk):break
  time.sleep(.001)
 first=time.monotonic();m.stdin.write('m 6 0\n');m.stdin.flush()
 for _ in range(50):m.stdin.write('m 1 0\n');m.stdin.flush();time.sleep(.002)
 time.sleep(.3);v=cli(c,'scroll.inspect',{'id':s});cli(c,'scroll.stop',{'id':s});m.stdin.write('q\n');m.stdin.flush();m.wait(5);time.sleep(.3);text=log.read_bytes()[off:].decode();(a/('phase-probe-'+str(n)+'.log')).write_text(text);success=bool(re.search('pointer put back by .* sent',text));r={'try':n,'id':s,'randomDelay':delay,'phase':'first observed bar repark, 1px/2ms burst','paused':v,'relativeCorrectionSucceeded':success,'relativeRefused':'relative motion refused' in text}
 with open(a/'phase-probes.jsonl','a') as f:f.write(json.dumps(r)+'\n')
 if success:break
