from pathlib import Path
import shutil,json
P=Path('/home/lab/work/s3a');out=P/'fixture-startup-attempt';out.mkdir()
for n in ['new-f-0','new-a-0','new-counter-0']:
 if (P/n).exists():(P/n).rename(out/n)
for n in ['new-f-0-fixture.log','new-a-0-fixture.log','new-counter-0-fixture.log','newcases.py.console','adversarial.py','late_fixture.py','fix6.py','newcases.py','latecases.py']:
 if (P/n).is_file():shutil.copyfile(P/n,out/n)
f=P/'fix6.py';s=f.read_text().replace('try: time.sleep(wait); return call()', 'try:\n        time.sleep(wait)\n        if f.poll() is not None:raise RuntimeError("Fixture exited before capture: "+str(cmd)+" exit="+str(f.returncode))\n        return call()');f.write_text(s)
(P/'fixture-startup-correction.json').write_text(json.dumps({'reason':'DejaVuSansMono font absent; fixture processes exited before capture','preserved':str(out),'qualifiedProductCapturesInThoseAttempts':0,'correction':'distro dejavu-sans-mono-fonts install; fixture live-process gate before capture'},indent=2))
print('failed fixtures preserved; live-process precondition added')
