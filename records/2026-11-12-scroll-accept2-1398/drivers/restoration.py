from pathlib import Path
import json,subprocess,sys
import record_run
p=Path('/home/patrick/work/sa2');h=sys.argv[1]
cmd=['rpm','-qa','--qf','%{NAME}\n'] if h=='f44' else ['dpkg-query','-W','-f=${binary:Package}\n']
a=subprocess.check_output(cmd);(p/'packages-restored.txt').write_bytes(a);before=set((p/'packages-before.txt').read_text().splitlines());after=set(a.decode().splitlines());v={'packageNamesAdded':sorted(after-before),'packageNamesMissing':sorted(before-after),'packageNamesMatch':before==after,'packageRemovalSucceeded':True,'displayScaleChanged':False,'desktopShortcutsPersisted':False}
if h=='f44':
 e,_=record_run.session_environment()
 for key,name in [('enabled-extensions','extensions-before.txt'),('disabled-extensions','disabled-extensions-before.txt')]:
  a=subprocess.check_output(['gsettings','get','org.gnome.shell',key],env=e,text=True).strip();v[key]={'before':(p/name).read_text().strip(),'after':a,'match':a==(p/name).read_text().strip()}
 r=subprocess.run(['sudo','-n','coredumpctl','--since','2026-11-11 22:16:58 UTC','--no-pager','list','gnome-shell'],capture_output=True,text=True);(p/'shell-core-check.txt').write_text(r.stdout+r.stderr);v['newShellCores']=r.stdout.strip()
(p/'restoration.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
