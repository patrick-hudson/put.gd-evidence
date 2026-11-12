from pathlib import Path
import json,subprocess,os,time
P=Path('/home/patrick/work/s3a');before=subprocess.check_output(['dpkg-query','-W','-f=${binary:Package} ${Version} ${db:Status-Abbrev}\n']);(P/'reference-package-before.txt').write_bytes(before)
with (P/'reference-chromium-install.log').open('w') as log:r=subprocess.run(['sudo','-n','apt-get','install','-y','chromium'],stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0
try:
 env=dict(os.environ,SF7=str(P),SF7_VNC='5900')
 for n in ['native-pr-reference.py','neutral-rust-reference.py']:
  with (P/(n+'.console')).open('w') as log:r=subprocess.run(['python3',str(P/n)],env=env,stdout=log,stderr=subprocess.STDOUT)
  print(n,r.returncode,flush=True)
finally:
 with (P/'reference-chromium-remove.log').open('w') as log:r=subprocess.run(['sudo','-n','apt-get','purge','-y','chromium'],stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0
 after=subprocess.check_output(['dpkg-query','-W','-f=${binary:Package} ${Version} ${db:Status-Abbrev}\n']);(P/'reference-package-after.txt').write_bytes(after);v={'packageVersionsMatch':set(before.decode().splitlines())==set(after.decode().splitlines()),'packageVersionsAdded':sorted(set(after.decode().splitlines())-set(before.decode().splitlines())),'packageVersionsMissing':sorted(set(before.decode().splitlines())-set(after.decode().splitlines()))};(P/'reference-followup-cleanup.json').write_text(json.dumps(v,indent=2));print(v,flush=True);assert v['packageVersionsMatch']
(P/'reference-followup.done').write_text('done')
