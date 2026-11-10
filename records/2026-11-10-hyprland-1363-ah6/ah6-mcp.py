import asyncio,json,os,sys,time,subprocess
from pathlib import Path
sys.path.insert(0,str(Path.home()/'work/i1363/tools/lab'))
from mcp_client import helper_session
R=sys.argv[1];D=sys.argv[2] if len(sys.argv)>2 else 'hyprland';K='/home/patrick/work/put.gd/work/lab-bootstrap-'+('m74' if D=='cinnamon' else 'omarchy')+'/identity';ROOT=Path.home()/'work/i1363';E=ROOT/'work/acceptance-1363'/R;E.mkdir(parents=True,exist_ok=True)
WR=E/'mcp-cli'
wrapper=f"""#!/usr/bin/python3
import sys,shlex,json
sys.path.insert(0,{str(ROOT/'tools/lab')!r})
import lab
with open({str(E/'mcp-cli-call-count')!r},"a") as counter:
 counter.write("x")
a=sys.argv[1:]
if "--params-stdin" in a:
 a.remove("--params-stdin");a.append(sys.stdin.read())
r=lab.guest_session({str(ROOT/'work/lab-runs'/R)!r},"putgd-cli "+shlex.join(a)+" || true",timeout=90)
sys.stdout.write(r)
sys.exit(0 if json.loads(r)["ok"] else 1)
"""
WR.write_text(wrapper)
WR.chmod(0o700)
async def main():
 rows=[]
 async with helper_session(str(ROOT/'tools/mcp/.venv/bin/putgd-mcp'),['--cli',str(WR),'--socket','/run/user/1000/putgd/session.sock','--timeout','90']) as s:
  async def call(name,args):
   rep=await s.call_tool(name,args);d=getattr(rep,'structured_content',None) or getattr(rep,'structuredContent',None) or json.loads(rep.content[-1].text);assert d['ok'],d;return d['result']
  tools={t.name for t in (await s.list_tools()).tools};assert 'perform_action' in tools
  for action,delay in [('monitor',None),('repeat',None),('region',10),('window',3),('monitor',5),('repeat',3),('desktop',0)]:
   if action=='window':
    script="import sys;sys.argv=['checks','ah6','/home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity','hyprland'];from pathlib import Path;exec(compile(Path('/tmp/p1363-checks.py').read_text().split('build = cli(')[0],'<driver>','exec')); print(guest(ENV+\"setsid -f foot --title=Acceptance1363 sh -c 'printf Acceptance1363; sleep 180' >/tmp/ah6-terminal.log 2>&1 </dev/null\"));time.sleep(2);print(guest(ENV+\"hyprctl dispatch focuswindow title:Acceptance1363\"));print(guest(ENV+'hyprctl activewindow -j'))"
    focused=subprocess.run(['python3','-c',script],check=True,capture_output=True,text=True);(E/'mcp-window-ready.json').write_text(focused.stdout)
   args={'action':action}
   if delay is not None:args['delay_seconds']=delay
   start=time.monotonic();got=await call('perform_action',args);op=got['operationId']
   if action=='region':
    # Same real virtual-input drag as the accepted desktop driver.
    script="import sys;sys.argv=['checks',"+repr(R)+","+repr(K)+","+repr(D)+"];from pathlib import Path;exec(compile(Path('/tmp/p1363-checks.py').read_text().split('build = cli(')[0],'<driver>','exec'));import time;time.sleep(1);drag(300,300,600,500)"
    subprocess.run(['python3','-c',script],check=True,capture_output=True)
   for _ in range(180):
    r=await call('get_operation',{'id':op})
    if r['state'] in ['completed','failed','cancelled','partial']:break
    await asyncio.sleep(.25)
   row={'args':args,'id':op,'state':r['state'],'error':r.get('error'),'seconds':time.monotonic()-start,'items':r.get('items',[])};rows.append(row);(E/'mcp-live.json').write_text(json.dumps(rows,indent=2));print(action,delay,r['state'],flush=True);assert r['state']=='completed',r
   subprocess.run(['python3','/tmp/p1363-gui.py',R,K,D,'fetch-op',op,'mcp-'+action+'-'+str(delay)],check=True,capture_output=True)
  count_file=E/'mcp-cli-call-count';before_invalid=len(count_file.read_bytes())
  invalid=[]
  for args in [{'action':'monitor','delay_seconds':4},{'action':'region','delay_seconds':-3},{'action':'clipboard','delay_seconds':3},{'action':'edit','delay_seconds':5},{'action':'record','delay_seconds':10}]:
   reply=await s.call_tool('perform_action',args);value=getattr(reply,'structured_content',None) or json.loads(reply.content[-1].text);assert not value['ok'] and value['error']['code']=='invalid_request',value;invalid.append({'args':args,'result':value})
  (E/'mcp-invalid-delays.json').write_text(json.dumps(invalid,indent=2));print('5 invalid delayed-action combinations rejected',flush=True)
  invalid_types=[]
  for delay in ['3',3.5]:
   reply=await s.call_tool('perform_action',{'action':'region','delay_seconds':delay});value=getattr(reply,'structured_content',None);assert value and not value.get('ok') and value['error']['code']=='invalid_request',reply;invalid_types.append({'delay':delay,'isError':reply.is_error,'structuredContent':value,'text':[c.text for c in reply.content if hasattr(c,'text')]})
  (E/'mcp-invalid-delay-types.json').write_text(json.dumps(invalid_types,indent=2));print('2 invalid delay types rejected',flush=True)
  after_invalid=len(count_file.read_bytes());assert after_invalid==before_invalid,(before_invalid,after_invalid);(E/'mcp-invalid-cli-count.json').write_text(json.dumps({'before':before_invalid,'after':after_invalid,'passed':True},indent=2));print('7 invalid cases never invoked the production CLI',flush=True)
asyncio.run(main())
