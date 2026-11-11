import sys,json,time,shlex,subprocess,traceback,os
from pathlib import Path
from PIL import Image
D=Path('/home/patrick/work/scn');B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
k=sys.argv[1];r=B/'repo/work/lab-runs'/(k+('cr2' if k=='k' else 'cn'));o=D/'ev'/(k+('cr2' if k=='k' else 'cn'));o.mkdir(parents=True,exist_ok=True)
def cmd(c,timeout=300):return lab.guest_session(r,c,timeout=timeout)
def shot(n):Image.open(lab.screenshot(r,'confirm-'+n)['path']).save(o/(n+'.png'))
def fixture(n,c,fn,delay=4):
 pid=int(cmd('nohup '+c+' > /tmp/v3/'+n+'.log 2>&1 < /dev/null & echo $!').strip())
 try:time.sleep(delay);shot(n+'-ready');fn()
 finally:cmd('kill '+str(pid));time.sleep(1)
def case(n,rect='100,100,960,600'):
 print(k,n,'START',time.strftime('%H:%M:%S'),flush=True);(o/(n+'.console')).write_text(cmd('python3 /home/lab/v3guest.py case '+n+' '+rect));shot(n+'-end');print(k,n,'DONE',flush=True)
def ruler(n,start=0,rows=600):fixture(n,'env SC_Y=100 python3 /home/lab/v3ruler.py --rows '+str(rows)+' --start '+str(start),lambda:case(n))
def browser(n,bottom):
 app='chromium --no-first-run --password-store=basic --user-data-dir=/tmp/v3/chromium --kiosk' if k=='o' else 'firefox --no-remote --profile /home/lab/v3firefox --kiosk'
 fixture(n,app+' file:///home/lab/'+('bottom.html' if bottom else 'v3ruler.html'),lambda:case(n,'0,0,1280,800'),18)
try:
 for i in range(3):ruler('long-bottom-%d'%i,23400)
 for kind,count in [('qt',3),('gtk',2)]:fixture(kind+'bottom','python3 /home/lab/v3text.py '+kind+' 1280 bottom',lambda:[case(kind+'1280-bottom-%d'%i,'0,100,1260,600') for i in range(count)])
 cmd('mkdir -p /home/lab/v3firefox; printf %s '+shlex.quote('user_pref("browser.aboutwelcome.enabled",false);user_pref("browser.shell.checkDefaultBrowser",false);user_pref("browser.startup.homepage_override.mstone","ignore");')+' > /home/lab/v3firefox/user.js')
 cmd("python3 -c "+shlex.quote("from pathlib import Path;p=Path('/home/lab/v3ruler.html');Path('/home/lab/bottom.html').write_text(p.read_text()+'<script>setTimeout(()=>{scrollTo(0,999999);document.title=\"BOTTOM \"+scrollY},1000)</script>')"))
 for i in range(3):browser('browser-bottom-%d'%i,True)
 ruler('half-off',12000)
 for i in range(3):ruler('native-%d'%i,0,60)
 for i in range(2):browser('browser-top-%d'%i,False)
 ruler('stop-top',23400)
 fixture('capflow','env SC_Y=100 python3 /home/lab/v3ruler.py --rows 600',lambda:(case('cap'),case('postcap')))
 # MCP uses the official SDK helper forwarding only to the production CLI.
 def mcp():
  off=int(cmd('stat -c %s /tmp/v3/helper.log').strip())
  p=subprocess.run([str(Path('/home/patrick/work/sf4/mcpvenv/bin/python')),str(D/'v3mcp.py'),k],capture_output=True,text=True,timeout=300);(o/'mcp.console').write_text(p.stdout+p.stderr);p.check_returncode()
  events=json.loads((D/('v3-'+k+'-mcp.json')).read_text());a=events[-1]['reply']['result'];(o/'mcp-events.json').write_text(json.dumps(events,indent=2))
  code="import json,hashlib,shutil;from pathlib import Path;p=Path('/tmp/v3');d=p/'cases/mcp';d.mkdir();a=json.loads(%r);(d/'result.json').write_text(json.dumps({'capture':a}));(d/'helper.log').write_bytes((p/'helper.log').read_bytes()[%d:]);sha=a['result']['sha256'];f=next(f for f in (p/'archive').rglob('*.png') if hashlib.sha256(f.read_bytes()).hexdigest()==sha);shutil.copyfile(f,d/'capture.png')"%(json.dumps(a),off)
  cmd('python3 -c '+shlex.quote(code))
 fixture('mcpfixture','env SC_Y=100 python3 /home/lab/v3ruler.py --rows 600 --start 23400',mcp)
 subprocess.run(['python3',str(D/'acc.py'),k,'cn','export'],check=True)
 (o/'campaign.done').write_text('done')
except Exception:(o/'campaign.error').write_text(traceback.format_exc());raise
