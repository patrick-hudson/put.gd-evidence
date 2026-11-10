import json,subprocess,time,sys
from pathlib import Path
base=Path.home()/'work/s1364s2'
with (base/'audio-observer.jsonl').open('a') as f:
 while not (base/(sys.argv[1] if len(sys.argv)>1 else 'campaign.done')).exists():
  names=subprocess.run(['pactl','list','short','sources'],capture_output=True,text=True).stdout
  row={'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'physicalInputs':[s.split('\t') for s in names.splitlines() if '\talsa_input.' in s]}
  f.write(json.dumps(row)+'\n');f.flush()
  if any(s[-1]!='SUSPENDED' for s in row['physicalInputs']):(base/'REAL-INPUT-ALERT.json').write_text(json.dumps(row)+'\n')
  time.sleep(2)
