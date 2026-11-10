import importlib.util,pathlib,subprocess,json,os
H=pathlib.Path.home();spec=importlib.util.spec_from_file_location('driver',H/'lab/record_run-hide-bar.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);env,desktop=m.session_environment()
report=dict(desktop=desktop,session=env.get('XDG_SESSION_TYPE'),uid=os.getuid(),kernel=os.uname().release)
for name,args in [('permissions',['hyprctl','getoption','ecosystem:enforce_permissions','-j']),('softwareCursor',['hyprctl','getoption','cursor:no_hardware_cursors','-j']),('monitors',['hyprctl','-j','monitors']),('audioSources',['pactl','list','short','sources']),('audioSinks',['pactl','list','short','sinks'])]:
 r=subprocess.run(args,env=env,capture_output=True,text=True);report[name]=dict(exit=r.returncode,stdout=r.stdout,stderr=r.stderr)
(H/'guest-identity.json').write_text(json.dumps(report,indent=1));print(report['permissions'])
