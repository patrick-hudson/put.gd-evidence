import asyncio,json,os
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
P=Path(os.environ.get('SFA_MCP_ROOT',str(Path.home()/'work/sfa15')))
async def main():
 params=StdioServerParameters(command=os.environ.get('SFA_MCP_PYTHON',str(P/'tools/mcp/.venv/bin/python')),args=['-m','share_mcp.server','--cli',str(P/'cli'),'--socket',os.environ.get('SFA_MCP_SOCKET',str(P/'r/putgd/session.sock'))],env=dict(os.environ,PYTHONPATH=str(P/'tools/mcp')))
 records=[];active=set()
 async with stdio_client(params) as (r,w):
  async with ClientSession(r,w) as s:
   await s.initialize()
   async def call(n,a):
    x=await s.call_tool(n,a);obj=x.model_dump(mode='json');records.append({'tool':n,'arguments':a,'response':obj});(P/'mcp-results.json').write_text(json.dumps(records,indent=1))
    data=json.loads(next(c.text for c in x.content if c.type=='text'))
    if getattr(x,'is_error',getattr(x,'isError',False)) or not data.get('ok'):raise RuntimeError('MCP production error: '+str(data.get('error',{}).get('code')))
    if n=='prepare_scroll_capture':active.add(data['result']['id'])
    if n=='control_scroll_capture' and a['command'] in ['stop','cancel']:active.discard(a['id'])
    return data
   try:
    x=await call('prepare_scroll_capture',{'rect':[240,200,1440,820],'driver':'user'});sid=x['result']['id']
    await call('control_scroll_capture',{'id':sid,'command':'start'})
    await call('get_scroll_capture',{'id':sid})
    await call('control_scroll_capture',{'id':sid,'command':'auto_scroll','on':True})
    await asyncio.sleep(2)
    await call('control_scroll_capture',{'id':sid,'command':'auto_scroll','on':False})
    await call('get_scroll_capture',{'id':sid})
    await call('control_scroll_capture',{'id':sid,'command':'stop'})
    await call('list_history',{'limit':200})
    x=await call('prepare_scroll_capture',{'rect':[240,200,1440,820],'driver':'user'});sid=x['result']['id']
    await call('control_scroll_capture',{'id':sid,'command':'start'})
    await call('control_scroll_capture',{'id':sid,'command':'cancel'})
    await call('list_history',{'limit':200})
   finally:
    for sid in list(active):
     try:await call('control_scroll_capture',{'id':sid,'command':'cancel'})
     except Exception as e:
      with (P/'mcp-cleanup-errors.log').open('a') as f:f.write(sid+' '+str(e)+'\n')
asyncio.run(main())
