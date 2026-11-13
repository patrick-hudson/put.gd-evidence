from pathlib import Path
import sys,subprocess,json,tempfile,os
sys.path.insert(0,str(Path.home()/'work/b1428/measure'));from text_proof import session_environment
E,_=session_environment(['gsd-power','gnome-shell']);sock=Path(E['XDG_RUNTIME_DIR'])/'putgd/session.sock';assert len(str(sock.resolve()).encode())<=107;assert not sock.exists(),'Quit resident before removing extension'
r=Path(tempfile.mkdtemp(prefix='c1428-',dir='/tmp'));env=dict(E,XDG_CONFIG_HOME=str(r/'config'),XDG_DATA_HOME=str(Path.home()/'.local/share'),XDG_CACHE_HOME=str(r/'cache'),XDG_STATE_HOME=str(r/'state'))
p=subprocess.run([str(Path.home()/'work/b1428/candidate.AppImage'),'--remove-gnome-extension'],env=env,capture_output=True,text=True,timeout=45)
out={'runtimeSocketUtf8Bytes':len(str(sock.resolve()).encode()),'removeExit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
assert p.returncode==0,out
for key,value in [('enabled-extensions',['background-logo@fedorahosted.org','appindicatorsupport@rgcjonas.gmail.com']),('disabled-extensions',['hkwitness@lab','putgd@put.gd'])]:subprocess.run(['gsettings','set','org.gnome.shell',key,str(value)],env=E,check=True)
a=Path.home()/'.local/share/putgd'
if a.exists():
 dst=Path.home()/'work/b1428'/('data-'+r.name+'-extension-removal');assert not dst.exists();a.rename(dst);out['retainedRemovalData']=str(dst)
out['extensionDirExists']=(Path.home()/'.local/share/gnome-shell/extensions/putgd@put.gd').exists();print(json.dumps(out,indent=2))
