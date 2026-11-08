import json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab
run=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();lab.verify_owned_guest(run)
script='''import os,stat,json,time,re
from pathlib import Path
seen=set();end=time.monotonic()+240
while time.monotonic()<end:
 for root in Path('/dev/shm').glob('n????????'):
  try:
   if not re.fullmatch('n[0-9a-f]{8}',root.name) or root.is_symlink() or root.stat().st_uid!=os.getuid() or stat.S_IMODE(root.stat().st_mode)!=0o700:continue
   for p in root.glob('fx-*/pattern.log'):
    if (p.parent/'owner').read_text()[:8]!=p.parent.name[3:]:continue
    rows=[]
    for line in p.read_text().splitlines():
     try:r=json.loads(line)
     except ValueError:continue
     if not isinstance(r,dict):continue
     row={k:r[k] for k in ('ok','state','rect','size','placed','monitorIndex') if k in r}
     if r.get('reason') in ('not_fullscreen_on_output','output_not_in_gtk3'):row['reason']=r['reason']
     if row:rows.append(row)
    record=dict(root=str(root),records=rows);encoded=json.dumps(record,sort_keys=True)
    if encoded not in seen:seen.add(encoded);print(encoded,flush=True)
  except (OSError,ValueError):pass
 time.sleep(.5)
'''
out.write_text(lab.guest_session(run,"python3 - <<'PY'\n"+script+"\nPY\n",timeout=260));print('pattern metadata saved',out)
