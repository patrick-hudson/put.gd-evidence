import asyncio,json,os,subprocess,time
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
base=Path.home()/'work/s1364s2';spec=json.loads((base/'picture-spec.json').read_text())
runtime=Path('/run/user/%d/s2a'%os.getuid());runtime.mkdir(mode=0o700,exist_ok=True)
socket_paths=[str(runtime/'putgd/session.sock')]
for address in os.environ.get('DBUS_SESSION_BUS_ADDRESS','').split(';'):
 for part in address.replace('unix:','').split(','):
  if part.startswith(('path=','abstract=')):socket_paths.append(part.split('=',1)[1])
assert all(len(p.encode())<=107 for p in socket_paths)
(base/'annotation-sockets.json').write_text(json.dumps({p:len(p.encode()) for p in socket_paths},indent=1)+'\n')
assert runtime.stat().st_uid==os.getuid() and runtime.stat().st_mode & 0o777==0o700
root=base/'root/usr/bin';python=base/'src/tools/mcp/.venv/bin/python';exe=base/'src/tools/mcp/.venv/bin/putgd-mcp'
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',XDG_RUNTIME_DIR=str(runtime))
for key,folder in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_STATE_HOME','state'),('XDG_CACHE_HOME','cache')]:
 p=base/'annotation'/folder;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
process=subprocess.Popen([str(root/'putgd')],env=env,stdout=(base/'annotation.log').open('w'),stderr=subprocess.STDOUT)
async def main():
 async with stdio_client(StdioServerParameters(command=str(exe),args=['--cli',str(root/'putgd-cli'),'--socket',str(runtime/'putgd/session.sock')],env=env)) as (read,write):
  async with ClientSession(read,write) as s:
   await s.initialize();log=[]
   async def call(name,args):
    reply=await s.call_tool(name,args)
    structured=getattr(reply,'structured_content',None)
    if structured:r=structured
    else:r=json.loads(next(c.text for c in reply.content if c.type=='text'))
    log.append({'tool':name,'arguments':args,'reply':r});(base/'annotation-mcp.json').write_text(json.dumps(log,indent=1)+'\n')
    if not r.get('ok',True):raise RuntimeError(r)
    return r.get('result',r)
   for item in spec:
    for attempt in range(60):
     try:op=(await call('open_editor',{'source':'file','path':item['source']}))['operationId'];break
     except Exception:
      if attempt==59:raise
      await asyncio.sleep(.5)
    for _ in range(60):
     try:
      view=await call('get_editor',{'id':op})
     except RuntimeError as error:
      if not isinstance(error.args[0],dict) or error.args[0].get('error',{}).get('code')!='editor_starting':raise
      await asyncio.sleep(.25);continue
     if view.get('phase')=='editing':break
     await asyncio.sleep(.25)
    await call('edit_image',{'id':op,'commands':item['commands']})
    await call('save_editor_copy',{'id':op,'path':item['output'],'overwrite':True})
    await call('cancel_editor',{'id':op})
    print('ANNOTATED',item['output'],flush=True)
try:asyncio.run(main())
finally:
 subprocess.run([str(root/'putgd-cli'),'ui.quit','{}'],env=env,capture_output=True)
 try:process.wait(15)
 except subprocess.TimeoutExpired:process.terminate();process.wait(10)
