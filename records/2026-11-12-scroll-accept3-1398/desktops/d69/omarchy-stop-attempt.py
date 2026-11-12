from pathlib import Path
import os,signal,time,json,sys
P=Path('/home/lab/work/s3a');owned=[]
for q in Path('/proc').iterdir():
 if not q.name.isdigit() or int(q.name)==os.getpid():continue
 try:
  args=(q/'cmdline').read_bytes().split(bytes([0]))
  if any(a.startswith((str(P)+'/').encode()) for a in args) or (q/'cwd').resolve()==P:owned.append({'pid':int(q.name),'args':[a.decode(errors='replace') for a in args if a]})
 except OSError:pass
# Stop controllers and owned fixtures first, then the private resident.
for v in owned:
 try:os.kill(v['pid'],15)
 except ProcessLookupError:pass
time.sleep(2)
(P/'unqualified-attempt.json').write_text(json.dumps({'reason':'Private runtime did not expose Hyprland compositor sockets; helper refused frame_source_unavailable before capture. Corrected driver supplies an owned symlink to real compositor sockets, retaining private putgd socket ownership checks.','terminatedExactProcesses':owned},indent=2));P.rename(P.with_name('s3h-attempt1'))
print('ATTEMPT_PRESERVED',flush=True)
