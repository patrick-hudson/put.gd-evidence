from pathlib import Path
import sys,shlex,json,base64,hashlib,shutil,re
B=Path(__file__).parent;G=B/'2026-11-12-scroll-accept2-1398';sys.path.insert(0,str(B.parent/'review'));import control
archives=[]
for host in ['m74','f44','d69']:
 code="""from pathlib import Path
import json,base64
r=Path('/home/patrick/work/scroll-accept2-archive');out={}
for p in r.iterdir():
 if p.is_file() and p.name.endswith('.json') and ('verified' in p.name or 'receipt' in p.name):out[p.name]=base64.b64encode(p.read_bytes()).decode()
print(json.dumps(out))
"""
 x=control.ssh(host,'python3 -c '+shlex.quote(code),capture_output=True,text=True,check=True)
 for n,v in json.loads(x.stdout).items():
  p=G/'cleanup'/host/n;p.parent.mkdir(exist_ok=True);p.write_bytes(base64.b64decode(v))
  j=json.loads(p.read_text())
  if 'archiveSha256' in j:
   stem=n.replace('-verified.json','');arc=stem+'.tgz';archives.append({'host':host,'archive':'/home/patrick/work/scroll-accept2-archive/'+arc,'sha256':j['archiveSha256'],'filesVerified':j.get('filesVerified',j.get('regularFilesVerified')),'verification':str(p.relative_to(G)),'restore':"mkdir -m 700 RESTORE_DIR && tar -xzf '"+'/home/patrick/work/scroll-accept2-archive/'+arc+"' -C RESTORE_DIR",'note':'Private regular-file archive; use the adjacent manifest to verify every restored file. Temporary authentication inputs are excluded from guest archives.'})
(G/'cleanup/cold-restore-index.json').write_text(json.dumps({'archives':archives,'preserveSources':True,'restoreOnHost':'Use a new private directory on the recorded builder; verify archive SHA-256 before extraction. No golden disks or credentials are in these archives.'},indent=2))
(G/'cleanup/README.md').write_text('# Cleanup receipts\n\nAll eleven disposable guests were retired after workstation export verification. Native test packages and extension lists were restored, locks released, original wall entries restored, and exact-file scratch deletion completed. See final-lock-status.json, wall-restoration.json, each host directory, and cap-proof/.\n\nPrivate raw-attempt archives are indexed in [cold-restore-index.json](cold-restore-index.json). Check the SHA-256 on its recorded builder, extract only into a new private directory, then compare regular files with the adjacent archive manifest. Guest authentication inputs were excluded and removed after guarded overlay retirement; immutable golden disks were preserved.\n')
for n in ['final-host-cleanup.py','finalize-packet.py']:shutil.copyfile(B/n,G/'drivers'/n)
idx=[]
for p in G.rglob('capture.png'):
 d=p.parent;rp=d/'result.json';result=json.loads(rp.read_text()) if rp.exists() else {};capture=result.get('capture',result);idx.append({'path':str(p.relative_to(G)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'operationId':capture.get('id',capture.get('operationId')),'endReason':capture.get('endReason'),'height':capture.get('height')})
(G/'case-index.json').write_text(json.dumps(idx,indent=2))
a=json.loads((G/'section-A-proof.json').read_text());a['guestCapReceiverFollowups']={k:{'exactPrefix':json.loads((G/'guests/cap-proof'/k/'verification.json').read_text())['pass'],'payloadEqualsPng':json.loads((G/'guests/cap-proof'/k/'upload-verification.json').read_text())['loopbackPayloadEqualsPng'],'uploaded':json.loads((G/'guests/cap-proof'/k/'workstation-verified.json').read_text())['uploaded'],'evidence':'guests/cap-proof/'+k} for k in 'obnk'};(G/'section-A-proof.json').write_text(json.dumps(a,indent=2))
print('indexed',len(idx),'capture PNGs and',len(archives),'cold archives')
