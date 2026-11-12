import asyncio,sys,os,json,time,subprocess,shlex,hashlib
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
k=sys.argv[1];b=Path(__file__).parent
ssh=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/d69/known_hosts','patrick@192.168.68.69']
marker='b.done' if k in ['b','n'] else 'browser-valid.done' if k=='k' else 'c.done'
while subprocess.run(ssh+['test -f /home/patrick/work/sa2vm/ev/sa2'+k+'/'+marker],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:time.sleep(3)
wrapper=b/('guest-cli-'+k);wrapper.write_text('#!/usr/bin/env python3\nimport subprocess,sys,shlex\nsys.exit(subprocess.run('+repr(ssh)+'+[shlex.join(["env","VM_RUN='+k+'","python3","/home/patrick/work/sa2vm/v3-mcp-cli.py"]+sys.argv[1:])],input=sys.stdin.buffer.read()).returncode)\n');wrapper.chmod(0o700)
subprocess.run(ssh+['python3 /home/patrick/work/sa2vm/guest-mcp-host.py '+k+' start'],check=True);time.sleep(3)
async def main():
 log=[]
 async with stdio_client(StdioServerParameters(command='/home/patrick/work/rolling-capture-research/acceptance/mcp/.venv/bin/putgd-mcp',args=['--cli',str(wrapper)],env=dict(os.environ,PYTHONPATH='/home/patrick/.t3/worktrees/put.gd/t3-958af5e2-83dc2e98e787ef61/tools/mcp'))) as (read,write):
  async with ClientSession(read,write) as s:
   await s.initialize()
   async def call(n,a):
    r=await s.call_tool(n,a);v=json.loads(next(x.text for x in r.content if x.type=='text'));log.append({'tool':n,'args':a,'reply':v});assert v['ok'],v;return v['result']
   a=await call('prepare_scroll_capture',{'rect':[100,100,960,600]});ident=a['id']
   while a['state']!='ready':await asyncio.sleep(.2);a=await call('get_scroll_capture',{'id':ident})
   await call('control_scroll_capture',{'id':ident,'command':'start'})
   for _ in range(800):
    a=await call('get_scroll_capture',{'id':ident})
    if a['state'] in ['done','failed','cancelled']:break
    await asyncio.sleep(.3)
 (b/('guest-'+k+'-mcp.json')).write_text(json.dumps(log,indent=2));assert a.get('result',{}).get('sha256'),a
 subprocess.run(ssh+['python3 /home/patrick/work/sa2vm/guest-mcp-host.py '+k+' save '+shlex.quote(json.dumps(a))],check=True)
 dest=b/('guest-'+k+'-mcp.png');subprocess.run(['scp',*ssh[1:-1],ssh[-1]+':/home/patrick/work/sa2vm/ev/sa2'+k+'/mcp-capture.png',str(dest)],check=True);assert hashlib.sha256(dest.read_bytes()).hexdigest()==a['result']['sha256']
 print(k,a['state'],a.get('endReason'),flush=True)
asyncio.run(main())
