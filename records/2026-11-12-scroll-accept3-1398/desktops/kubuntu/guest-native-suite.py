from pathlib import Path
import subprocess,json
P=Path('/home/lab/work/s3a');jobs=[['controls7.py','ruler','text','resize'],['more-a.py'],['startcancel.py','b'],['browsercases.py'],['capmore.py'],['notices.py','b'],['timer-case.py'],['warning-proof.py','b']];results=[]
for args in jobs:
 with (P/('suite-'+args[0]+'.console')).open('w') as log:r=subprocess.run(['python3',str(P/args[0]),*args[1:]],stdout=log,stderr=subprocess.STDOUT)
 results.append({'args':args,'exitCode':r.returncode});(P/'suite-status.json').write_text(json.dumps(results,indent=2));print(args,r.returncode,flush=True)
(P/'suite.done').write_text('done')
