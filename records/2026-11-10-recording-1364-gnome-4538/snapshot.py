import json,subprocess,sys,time
from pathlib import Path
base=Path.home()/'work/s1364s2';sys.path.insert(0,str(base/'lab'));import record_run
from gi.repository import Gio
stage=sys.argv[1];env,desktop=record_run.session_environment()
def cmd(*a):return subprocess.run(a,env=env,capture_output=True,text=True).stdout.strip()
settings=Gio.Settings.new('org.gnome.shell')
result={'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'desktop':desktop,'settings':{k:settings.get_value(k).print_(True) for k in ['enabled-extensions','disabled-extensions']},'package':cmd('rpm','-q','putgd'),'extension':cmd('gnome-extensions','info','putgd@put.gd'),'defaultSource':cmd('pactl','get-default-source'),'defaultSink':cmd('pactl','get-default-sink'),'sources':cmd('pactl','list','short','sources'),'modules':cmd('pactl','list','short','modules'),'processes':cmd('ps','-u',str(__import__('os').getuid()),'-o','pid=,comm='),'gnomeVersion':cmd('gnome-shell','--version'),'os':cmd('cat','/etc/fedora-release'),'load':Path('/proc/loadavg').read_text().strip()}
(base/(stage+'.json')).write_text(json.dumps(result,indent=1)+'\n'); print(json.dumps({k:result[k] for k in ['package','extension','defaultSource','defaultSink','gnomeVersion','load']}));print(result['processes'])
