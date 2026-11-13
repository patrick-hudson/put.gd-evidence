from pathlib import Path
import os,sys,json,subprocess,hashlib,shlex,stat
h=Path.home();r=h/'work/ocr-corpus-1428';host=sys.argv[1];roots=[r/'candidate-file-code-appimage-checks/d',h/'work/i8m/appimage/d',h/'work/i8g4/ad',h/'work/i8g4b/ad'] if host=='m74' else [h/'work/i8dai/d',h/'work/i8dp/appimage/d',h/'work/i8dp2/appimage/d'];index=r/'candidate-m74-pipeline/index.json'
if host=='m74' and index.exists():roots.extend(Path(x['receipt']).parent/'data' for x in json.loads(index.read_text()))
rows=[]
for root in roots:
 record=root/'putgd/file-manager/appimage.owned';script=record.parent/'putgd-upload'
 if not script.exists():continue
 info=script.lstat();assert stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and not script.is_symlink();text=script.read_text();assert 'X-putgd-Managed=true' in text;units=[shlex.split(line.split('=',1)[1])[0] for line in text.splitlines() if line.startswith('watch_unit=')];assert len(units)==1 and units[0].startswith('putgd-');unit=units[0];p=subprocess.run(['/bin/sh',str(script),'--stop-watch'],capture_output=True,text=True,timeout=30);env=os.environ|{'XDG_RUNTIME_DIR':'/run/user/'+str(os.getuid())};q=subprocess.run(['systemctl','--user','is-active',unit+'.path'],env=env,capture_output=True,text=True);row={'script':str(script),'sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'unit':unit,'stopExit':p.returncode,'pathUnitActive':q.stdout.strip(),'scope':'Stopped only this owned private AppImage integration removal watch; menu files remain private, no actual user menu altered.'};rows.append(row);print(unit,p.returncode,q.stdout.strip(),flush=True)
(r/'candidate-integration-watch-cleanup.json').write_text(json.dumps({'host':host,'rows':rows,'allStopped':all(x['stopExit']==0 and x['pathUnitActive']!='active' for x in rows)},indent=2))
