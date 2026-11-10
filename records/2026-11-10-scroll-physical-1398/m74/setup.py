import os,sys,json,subprocess,time,pathlib
sys.path.insert(0,'/tmp/sp1398');import record_run
a=pathlib.Path('/tmp/sp1398');env,desktop=record_run.session_environment()
for n in ('config','data','cache','state','runtime','archive'):(a/n).mkdir(mode=0o700,exist_ok=True)
for k,n in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state'),('XDG_RUNTIME_DIR','runtime')]:env[k]=str(a/n)
env.update(PIPEWIRE_RUNTIME_DIR='/run/user/1000',PULSE_SERVER='unix:/run/user/1000/pulse/native',PUTGD_RECORD_DEBUG_LOG=str(a/'helper.log'))
print('socket bytes',len(str(a/'runtime/putgd/session.sock').encode()))
assert len(str(a/'runtime/putgd/session.sock').encode())<=107
(a/'env.json').write_text(json.dumps(env));(a/'desktop.json').write_text(json.dumps({'desktop':desktop,'session':subprocess.getoutput('loginctl list-sessions'),'build':json.loads(subprocess.check_output(['putgd-cli','--version-json']))},indent=2))
f=open(a/'resident.log','a');p=subprocess.Popen(['putgd','--background'],env=env,stdout=f,stderr=f,start_new_session=True);(a/'resident.pid').write_text(str(p.pid))
def rpc(m,p={}):
 r=subprocess.run(['putgd-cli','--socket',str(a/'runtime/putgd/session.sock'),m,json.dumps(p)],env=env,text=True,capture_output=True);o=json.loads(r.stdout);assert o['ok'],o;return o['result']
for _ in range(100):
 if (a/'runtime/putgd/session.sock').exists():break
 time.sleep(.1)
s=rpc('settings.get');(a/'original-private-settings.json').write_text(json.dumps(s))
print(rpc('settings.save',{'document':dict(s['document'],archive=dict(s['document']['archive'],keepUploads=True,root=str(a/'archive'))),'expectedRevision':s['metadata']['observedRevision']}))
print(rpc('scroll.capabilities'))
