import sys,json,time
from pathlib import Path
sys.path.insert(0,'work/ta1541');from check import Check
c=Check();p=c.t.physical
v=p.ssh(p.run,'sudo -n apt-get install -y /tmp/t541-candidate.deb\n');Path('work/ta1541/install.log').write_text(v)
p.put(p.run,'work/ta1541/receiver.py','/tmp/t541-receiver.py')
d=json.loads(Path('config/development.example.json').read_text());d['profiles']=[];d['actions']={x:{'destination':'local','profileId':None,'shortcut':''} for x in ['region','window','desktop','monitor','scroll','edit','clipboard']};d['actions']['record']={'shortcut':''};d['archive'].update(root='/tmp/t541/files',keepUploads=True);d['preferences'].update(launchAtLogin=False,notifications=False,updates={'check':False})
from tools.lab.http_receivers.check_uploads import synthetic_png
payload=synthetic_png();Path('work/ta1541/payload.png').write_bytes(payload)
code='''import subprocess,json,shutil
from pathlib import Path
r=Path('/tmp/t541');r.mkdir(mode=0o700)
for s in ('runtime','config','data','cache','state','files','rx'):(r/s).mkdir(mode=0o700)
p=r/'runtime/putgd/session.sock';assert len(str(p).encode())<=107;print('sessionSocketBytes',len(str(p).encode()))
q=r/'config/putgd';q.mkdir();(q/'config.json').write_text(json.dumps(DOCUMENT))
sx=Path.home()/'putgd-lab/http-receivers/sxcu/zipline.sxcu';shutil.copyfile(sx,r/'rx/upstream.sxcu');u=json.loads(sx.read_text());u['Headers']={};u['Name']='PR1541 lab HTTP receiver';u['RequestURL']='http://192.168.68.72:18432/upload';(r/'rx/uploader.sxcu').write_text(json.dumps(u));(r/'rx/control.json').write_text('{"fail":true}')
f=open(r/'cover.log','w');s=subprocess.Popen(['sleep','1800'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,start_new_session=True);cover=subprocess.Popen(['python3','/home/patrick/work/ta1532-src/tools/lab/cover_player.py','play','--output','HDMI-A-1'],stdin=s.stdout,stdout=f,stderr=f,start_new_session=True);s.stdout.close()
f=open(r/'rx/server.log','w');rx=subprocess.Popen(['python3','/tmp/t541-receiver.py',str(r/'rx')],stdin=subprocess.DEVNULL,stdout=f,stderr=f,start_new_session=True)
pids={'sleep':s.pid,'cover':cover.pid,'receiver':rx.pid};(r/'pids.json').write_text(json.dumps(pids));print(json.dumps(pids))
'''.replace('DOCUMENT',repr(d))
v=c.session("python3 - <<'SETUP'\n"+code+'SETUP\n');Path('work/ta1541/setup.txt').write_text(v);print(v)
p.put(p.run,'work/ta1541/payload.png','/tmp/t541/503-payload.png');p.put(p.run,'work/ta1541/payload.png','/tmp/t541/crash-held.png')
time.sleep(2);print(c.session('python3 /home/patrick/work/ta1532-src/tools/lab/cover_player.py precheck --port 5900'))
pids=json.loads(v.splitlines()[-1]);print(c.js('for(const w of workspace.windowList()){if(w.pid==='+str(pids['cover'])+'){w.fullScreen=false;w.keepAbove=false;w.keepBelow=true;w.setMaximize(true,true);}}'))
print(c.shell('nohup putgd --background > /tmp/t541/app.log 2>&1 < /dev/null & echo $! > /tmp/t541/resident.pid'))
time.sleep(2);diag=c.call('diagnostics');assert diag['build']['gitTree']=='3de3ae46f4d3287e197a2b62121c9f3c953fa105';Path('work/ta1541/diagnostics.json').write_text(json.dumps(diag,indent=2));print(diag['build'])
c.call('settings.importUploader',{'path':'/tmp/t541/rx/uploader.sxcu','expectedRevision':c.call('settings.get')['metadata']['acceptedRevision'],'profileId':'ta1541-http','credentialMode':'session','allowInsecureHttp':True})
c.call('ui.show',{'view':'history'});c.size(1440)
a=c.call('upload.files',{'paths':['/tmp/t541/503-payload.png'],'profileId':'ta1541-http'});Path('work/ta1541/operations.json').write_text(json.dumps({'first':a['operationId']}));time.sleep(2);op=c.call('operation.inspect',{'id':a['operationId']});print(op['state'],op['error'])
c.click(1522,1051,'right');c.frame('01-503-tray')
