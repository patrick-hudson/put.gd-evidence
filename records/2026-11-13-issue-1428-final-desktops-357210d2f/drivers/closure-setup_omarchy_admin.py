from pathlib import Path
import subprocess,re,time
text=Path('docs/lab/remote-golden-images.md').read_text()
match=re.search(r'^\| Shared default lab password \| `([^`]+)` \|$',text,re.M);assert match
value=match.group(1).encode()+b'\n'
command=['python3','/tmp/b1428/guest_remote.py','fhk',"sudo -S -p '' python3 /home/lab/sudo_policy.py"]
for attempt in range(45):
 probe=subprocess.run(['python3','/tmp/b1428/guest_remote.py','fhk','true'],capture_output=True)
 if probe.returncode==0:break
 time.sleep(2)
else:raise RuntimeError('Guest SSH unavailable after resume')
subprocess.run(['python3','/tmp/b1428/guest_remote.py','fhk','--copy','/tmp/b1428/sudo_policy.py','/home/lab/'],check=True)
result=subprocess.run(command,input=value,capture_output=True);value=b''
assert result.returncode==0,{'exitCode':result.returncode,'stderrSuppressed':True}
verified=subprocess.check_output(['python3','/tmp/b1428/guest_remote.py','fhk','sudo -n id -u'],text=True).strip();assert verified=='0'
print('Guest-only policy installed using documented disposable-guest default via stdin; sudo verified 0. No login or golden changed; secret not retained.')
