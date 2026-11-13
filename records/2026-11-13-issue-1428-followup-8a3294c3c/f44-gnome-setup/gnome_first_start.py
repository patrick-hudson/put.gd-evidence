from pathlib import Path
from types import SimpleNamespace
import sys,json,subprocess,os,signal,time,ast
sys.path.insert(0,str(Path(__file__).parent/'measure') if (Path(__file__).parent/'measure').exists() else str(Path(__file__).parent))
from text_proof import Run
app,cli=sys.argv[1:3];r=Run(SimpleNamespace(leader=['gsd-power','gnome-shell'],real_profile=False,app=app,cli=cli,input_socket='start',desktop='GNOME-first-start-8a',hotkey=''))
out={'setupOnly':True,'socketPathsUtf8Bytes':r.receiptSocketLengths}
def gs(key):
 p=subprocess.run(['gsettings','get','org.gnome.shell',key],env=r.env,capture_output=True,text=True,check=True);v=p.stdout.strip();return ast.literal_eval(v.removeprefix('@as '))
try:
 out['before']={k:gs(k) for k in ['enabled-extensions','disabled-extensions']}
 r.spawn([app,'--background']);r.wait(lambda:Path(r.socket).exists(),'resident');time.sleep(3)
 out['pid']=r.resident_pid();out['exe']=os.readlink('/proc/'+str(out['pid'])+'/exe');out['diagnostics']=r.cli('diagnostics')['result'];out['capabilities']=r.cli('capabilities')['result']
 # Explicit test enablement, retaining every unrelated extension and its order.
 uuid='putgd@put.gd';enabled=gs('enabled-extensions');disabled=gs('disabled-extensions');disabled=[x for x in disabled if x!=uuid]
 if uuid not in enabled:enabled.append(uuid)
 for k,v in [('disabled-extensions',disabled),('enabled-extensions',enabled)]:subprocess.run(['gsettings','set','org.gnome.shell',k,str(v)],env=r.env,check=True)
 out['after']={k:gs(k) for k in ['enabled-extensions','disabled-extensions']}
finally:
 try:r.cli('ui.quit')
 except Exception as e:out['quitError']=str(e)
 time.sleep(2)
 for p in r.started:
  if p.poll() is None:
   try:os.killpg(p.pid,signal.SIGTERM)
   except ProcessLookupError:pass
 if r.appimage_user_data and r.appimage_user_data.exists():
  p=Path.home()/'work/b1428';p.mkdir(parents=True,exist_ok=True,mode=0o700);dst=p/('data-'+r.root.name+'-setup');assert not dst.exists();r.appimage_user_data.rename(dst);out['retainedAppData']=str(dst)
 (r.root/'setup.json').write_text(json.dumps(out,indent=2));print('SETUP '+str(r.root/'setup.json'),flush=True)
