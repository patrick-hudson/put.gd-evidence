import datetime,json,subprocess
from pathlib import Path
r=Path.home()/'work/ocr-integration-bcb-artifacts'
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':'k72','scope':'Only disposable containers created for packaging #1438; retained installer inputs, source exports, snapshots, commands and receipts are not removed','containers':[]}
for kind in ('deb','rpm','arch','native-size'):
 name='pg1438-'+(kind+'-clean' if kind!='native-size' else kind)
 info=json.loads(subprocess.check_output(['podman','inspect',name],text=True))[0]
 assert info['Name']==name and info['Config']['Cmd']==['tail','-f','/dev/null']
 if kind!='native-size':assert info['Id']==(r/(kind+'-container-id')).read_text().strip()
 else:assert any(m.get('Source')==str(Path.home()/'work/ocr-pkg-1438-artifacts') for m in info['Mounts'])
 row={'name':name,'id':info['Id'],'image':info['ImageName'],'beforeStatus':info['State']['Status'],'processesBefore':subprocess.check_output(['podman','top',name,'hpid','args'],text=True)}
 subprocess.run(['podman','stop','--time','10',info['Id']],check=True,capture_output=True,text=True)
 subprocess.run(['podman','rm',info['Id']],check=True,capture_output=True,text=True)
 row['removed']=True;receipt['containers'].append(row)
assert not any('putgd-26.1113.4805-dev+gbcb868f9ac5b-x86_64.AppImage' in s for s in Path('/proc/self/mountinfo').read_text().splitlines())
receipt['ownedAppImageUnmounted']=True
(r/'cleanup-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('Four exact owned containers retired; inputs and evidence retained; no AppImage mount left.')
