import asyncio,json,sys,os,subprocess,time,hashlib,shlex
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
base=Path(__file__).parent;host=sys.argv[1];ip={'d69':'69','f44':'70','m74':'74'}[host]
ssh=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+host+'/known_hosts','patrick@192.168.68.'+ip]
wrapper=base/('cli-'+host);wrapper.write_text('#!/usr/bin/env python3\nimport subprocess,sys,shlex\nsys.exit(subprocess.run('+repr(ssh)+'+[shlex.join(["putgd-cli"]+sys.argv[1:])],input=sys.stdin.buffer.read()).returncode)\n');wrapper.chmod(0o700)
subprocess.run(ssh+['cd /home/patrick/work/pc2 && python3 extras3.py mcpfixture'],check=True)
time.sleep(3)
offset=int(subprocess.check_output(ssh+["stat -c %s /home/patrick/work/pc2/helper.log"],text=True).strip())
async def main():
 log=[]
 async with stdio_client(StdioServerParameters(command='/home/patrick/work/rolling-capture-research/acceptance/mcp/.venv/bin/putgd-mcp',args=['--cli',str(wrapper),'--socket','/home/patrick/work/pc2/r/putgd/session.sock'],env=dict(os.environ,PYTHONPATH='/home/patrick/.t3/worktrees/put.gd/t3-ff3c2a74-709db7d638d7743e/tools/mcp'))) as (read,write):
  async with ClientSession(read,write) as s:
   await s.initialize()
   async def call(n,a):
    r=await s.call_tool(n,a);v=json.loads(next(x.text for x in r.content if x.type=='text'));log.append({'tool':n,'args':a,'reply':v});assert v['ok'],v;return v['result']
   a=await call('prepare_scroll_capture',{'rect':[100,200,960,600]});i=a['id'];await asyncio.sleep(1)
   await call('control_scroll_capture',{'id':i,'command':'start'})
   for _ in range(600):
    a=await call('get_scroll_capture',{'id':i})
    if a['state'] in ('done','failed','cancelled'):break
    await asyncio.sleep(.3)
 (base/(host+'-mcp.json')).write_text(json.dumps(log,indent=2));print(host,a['state'],a.get('endReason'))
 if a.get('result',{}).get('sha256'):
  sha=a['result']['sha256'];subprocess.run(ssh+['cd /home/patrick/work/pc2 && python3 mcp_verify.py '+sha],check=True)
  out=base/(host+'-mcp.png');subprocess.run(['scp',*ssh[1:-1],ssh[-1]+':/home/patrick/work/pc2/mcp/capture.png',str(out)],check=True)
  assert hashlib.sha256(out.read_bytes()).hexdigest()==sha
 code="from pathlib import Path;import json;p=Path('/home/patrick/work/pc2');d=p/'mcp';r=json.loads((d/'result.json').read_text());r['capture']=json.loads(%r);(d/'result.json').write_text(json.dumps(r,indent=2));(d/'helper.log').write_bytes((p/'helper.log').read_bytes()[%d:])"%(json.dumps(a),offset)
 subprocess.run(ssh+['python3 -c '+shlex.quote(code)],check=True)
 subprocess.run(ssh+['kill $(cat /home/patrick/work/pc2/mcp-fixture.pid)'],check=True)
asyncio.run(main())
