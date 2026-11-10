import asyncio,json,sys,os,time
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
 r=sys.argv[1];env=dict(os.environ,VM_RUN=r);out=Path('/home/patrick/work/svm1398')/(r+'-mcp.json');events=[]
 params=StdioServerParameters(command='/home/patrick/work/svm1398/repo/tools/mcp/.venv/bin/putgd-mcp',args=['--cli','/home/patrick/work/svm1398/vm_mcp_cli.py'],env=env)
 async with stdio_client(params) as (read,write):
  async with ClientSession(read,write) as session:
   await session.initialize()
   async def call(name,args):
    v=await session.call_tool(name,args);obj=json.loads(v.content[0].text);events.append({'tool':name,'arguments':args,'reply':obj});out.write_text(json.dumps(events,indent=2));return obj['result']
   rect=[0,0,608 if r=='o' else 1280,800]
   a=await call('prepare_scroll_capture',{'rect':rect,'max_height':2000});i=a['id']
   for _ in range(100):
    a=await call('get_scroll_capture',{'id':i})
    if a['state']=='ready':break
    await asyncio.sleep(.2)
   await call('control_scroll_capture',{'id':i,'command':'start'})
   for _ in range(100):
    a=await call('get_scroll_capture',{'id':i})
    if a['state'] in ['done','failed','cancelled']:break
    await asyncio.sleep(.3)
   if a['state'] not in ['done','failed','cancelled']:await call('control_scroll_capture',{'id':i,'command':'cancel'})
asyncio.run(main())
