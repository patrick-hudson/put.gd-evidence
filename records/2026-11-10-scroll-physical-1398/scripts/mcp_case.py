import asyncio,json,sys,os,subprocess,time
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
base=Path(__file__).resolve().parent;host=sys.argv[1];wrapper=base/('cli-'+host)
opts=['-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+host+'/known_hosts'];ip={'d69':'69','f44':'70','m74':'74'}[host]
wrapper.write_text('#!/usr/bin/env python3\nimport subprocess,sys,shlex\nsys.exit(subprocess.run('+repr(['ssh']+opts+['patrick@192.168.68.'+ip])+ '+[shlex.join(["putgd-cli"]+sys.argv[1:])],input=sys.stdin.buffer.read()).returncode)\n');wrapper.chmod(0o700)
async def main():
 log=[]
 async with stdio_client(StdioServerParameters(command=str(base/'mcp/.venv/bin/putgd-mcp'),args=['--cli',str(wrapper),'--socket','/tmp/sp1398/runtime/putgd/session.sock'])) as (read,write):
  async with ClientSession(read,write) as s:
   await s.initialize()
   async def call(name,args):
    r=await s.call_tool(name,args);v=json.loads(next(x.text for x in r.content if x.type=='text'));log.append({'tool':name,'args':args,'reply':v});assert v['ok'],v;return v['result']
   r=await call('prepare_scroll_capture',{'rect':[100,100,960,600]});ident=r['id'];await asyncio.sleep(1)
   await call('control_scroll_capture',{'id':ident,'command':'start'})
   for _ in range(500):
    r=await call('get_scroll_capture',{'id':ident})
    if r['state'] in ('done','failed','cancelled'):break
    await asyncio.sleep(.3)
 (base/(host+'-mcp.json')).write_text(json.dumps(log,indent=2));print(host,r)
asyncio.run(main())
