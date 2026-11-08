import sys,os,json,time,hashlib,importlib.util,shlex
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
spec=importlib.util.spec_from_file_location('sp','work/sp/pass.py');m=importlib.util.module_from_spec(spec);sys.modules['sp']=m;spec.loader.exec_module(m)
run,out,desktop,pkg,host=sys.argv[1:];c=m.Context(Path(run).resolve(),out,desktop,pkg,host,'local');result={}
def work():
 service=c.fixture('loopback-s3');s=c.scope;s.patch({'preferences':{'notifications':False},'captureDefaults':{'destination':'upload','profileId':service.profile_id,'publicationMode':'share'}})
 name='scripted-proof.txt';data=b'putgd real file-manager right-click upload\n';path=s.root+'/files/'+name;s.write(path,data)
 # The entry follows the running resident, and the manager must discover the
 # same per-user entries as it; native packages also have system entries.
 manager='nautilus' if desktop=='omarchy-hyprland' else 'nemo' if desktop=='ubuntu-budgie-2604' else 'dolphin'
 # A fresh VM may run Nemo's desktop daemon. Quit only its disposable VM instance.
 if manager in ('nautilus','nemo'):c.shell(manager+' --quit');time.sleep(.5)
 env=dict(s._environment);p=s.launch([manager,'--new-window',s.root+'/files'] if manager=='nautilus' else [manager,s.root+'/files'],environment=env,name='file-manager')
 time.sleep(3);c.frame('file-manager-ready');before={o['id'] for o in c.call('operation.recent')['operations']}
 stage=dict(run=str(c.target.run),root=c.target.root,scope=s.root,manager=manager,filename=name)
 (c.out/'input-stage.json').write_text(json.dumps(stage));print('READY_REAL_RIGHT_CLICK',manager,flush=True)
 fresh=c.wait(lambda:next((o['id'] for o in c.call('operation.recent')['operations'] if o['id'] not in before),None),'real right-click menu upload',timeout=240)
 d,remote=m.complete(c,fresh,'right-click-upload');m.object_check(c,d,remote);assert remote==data and d['name']==name;c.call('ui.show',{'view':'history'});c.frame('right-click-upload-history');return {'manager':manager,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'realRightClick':True}
try:m.cell(c,result,'file_manager_upload','real file-manager right click, menu selection via Wayland pointer',work)
finally:c.close()
