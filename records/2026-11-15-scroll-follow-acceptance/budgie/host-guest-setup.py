from pathlib import Path
import subprocess,shlex,os,shutil
P=Path.home()/'work/sfa15/guest-h'
source=P/'native-source';assert not source.exists();source.mkdir()
for f in P.glob('*.py'):
 if f.name!='accept.py':shutil.copyfile(f,source/f.name)
(P/'live7.py').write_bytes((source/'live7-native-viewport.py').read_bytes())
import accept as A
(P/'cli').write_text('''#!/usr/bin/python3
import sys,subprocess,shlex,json
from pathlib import Path
r=Path.home()/"work/sfa15/repo/work/lab-runs/sfa15h";s=json.loads((r/"state.json").read_text())
a=["ssh","-i",str(r/"identity"),"-o","IdentitiesOnly=yes","-o","BatchMode=yes","-o","StrictHostKeyChecking=yes","-o","UserKnownHostsFile="+s["known_hosts"],"-p",str(s["ssh_port"]),"lab@127.0.0.1",shlex.join(["/home/lab/work/sfa15/cli",*sys.argv[1:]])]
sys.exit(subprocess.run(a).returncode)
''');(P/'cli').chmod(0o700)
for name,target in [('umouse.py','umouse-native.py'),('ukey.py','ukey-native.py'),('ukey-ready.py','ukey-ready-native.py')]:
 (P/name).write_text('import subprocess,sys,shlex\nimport accept as A\nsys.exit(subprocess.run([*A.SSH,shlex.join(["python3",A.GP+"/'+target+'"]) ]).returncode)\n')
for name in ['pages-relative.py','pause-relative.py','extra-relative.py','user-script-recovery.py','auto-script-recovery.py','mixed-focused.py']:
 p=P/name;s=p.read_text().replace("['sudo','-n','python3',","['python3',");p.write_text(s)
s=(source/'trial-native-pointer.py').read_text().replace("['sudo', '-n', 'python3',","['python3',")
i=s.index('def flat():');j=s.index('def now_ms():',i)
s=s[:i]+'''def flat():
    import accept as A
    return A.remote("flat")
def native_pointer():
    import accept as A
    return A.remote("pointer")

'''+s[j:];(P/'trial_relative.py').write_text(s)
(P/'relative-control.py').write_bytes((source/'relative-control-native.py').read_bytes())
s=(P/'pages-relative.py').read_text();needle='S.Driver=Driver'
old="left = subprocess.run(['pgrep', '-x', 'putgd-record'], capture_output=True, text=True).stdout.split()"
new="left = A.remote('helper-pids')"
addition='\nif hasattr(A,"remote"):\n import inspect\n S.A=A\n _run=inspect.getsource(S.run)\n _run=_run.replace('+repr(old)+','+repr(new)+')\n exec(_run,S.__dict__)\n'
assert s.count(needle)==1;(P/'pages-relative.py').write_text(s.replace(needle,needle+addition))
subprocess.run(['tar','-xf',str(P/'mcp.tar')],cwd=P,check=True)
args=['systemd-run','--user','--unit=sfa15h-transport','--collect','/usr/bin/ssh','-NT',*A.SSH[1:-1],'-o','ExitOnForwardFailure=yes','-o','ServerAliveInterval=30','-L','127.0.0.1:28291:127.0.0.1:28291','-R','127.0.0.1:5900:127.0.0.1:5940',A.SSH[-1]]
subprocess.run(args,check=True)
print('Installed host transport scripts and pinned MCP source; no host product/browser launched')
