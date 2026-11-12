from pathlib import Path
import subprocess,json,re
b=Path('/tmp/p4a')
for h in ['d69','k72','m74','f44']:
 logs=[b/(h+'-driver.log')]+([b/n for n in ['k72-diagnostic.log','k72-inspection.log','k72-cleanup.log']] if h=='k72' else [])
 paths=[]
 for f in logs:
  if f.exists():paths+=re.findall(r'receipt on the host: (/[^\n]+)',f.read_text())
 out=[]
 for p in paths:
  r=subprocess.run(['python3',str(b/'remote.py'),h,'cat '+p],capture_output=True,text=True,check=True)
  raw=json.loads(r.stdout)
  # Receipts can contain unrelated pre-existing process command lines; keep raw private.
  dest=b/'new'/h/'receipts';dest.mkdir(exist_ok=True)
  (dest/Path(p).name).write_text(r.stdout)
  out.append({'path':p,'keys':list(raw)})
 print(h,out)
