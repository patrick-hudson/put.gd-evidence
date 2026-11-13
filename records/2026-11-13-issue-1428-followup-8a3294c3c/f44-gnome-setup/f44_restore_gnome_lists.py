from pathlib import Path
import sys,subprocess,json
sys.path.insert(0,str(Path.home()/'work/b1428/measure'));from text_proof import session_environment
E,_=session_environment(['gsd-power','gnome-shell'])
base={'enabled-extensions':['background-logo@fedorahosted.org','appindicatorsupport@rgcjonas.gmail.com'],'disabled-extensions':['hkwitness@lab','putgd@put.gd']}
for k,v in base.items():subprocess.run(['gsettings','set','org.gnome.shell',k,str(v)],env=E,check=True)
# Probe only return codes/settings, never dump a whole session environment.
probe=[]
for label,env in [('real',E),('private',dict(E,XDG_RUNTIME_DIR='/tmp/tp-d6hb3h7h/rt',XDG_CONFIG_HOME='/tmp/tp-d6hb3h7h/config',XDG_DATA_HOME='/home/patrick/.local/share'))]:
 p=subprocess.run(['systemctl','--user','show-environment'],env=env,capture_output=True,text=True)
 g=subprocess.run(['gsettings','get','org.gnome.shell','enabled-extensions'],env=env,capture_output=True,text=True)
 probe.append({'case':label,'systemctlExit':p.returncode,'systemctlError':p.stderr.strip(),'gsettingsEnabled':g.stdout.strip()})
print(json.dumps({'restoredBaseline':base,'probe':probe},indent=2))
