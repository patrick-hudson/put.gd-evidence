from pathlib import Path
import os,subprocess,sys
P=Path('/home/patrick/work/s3a');ids=[]
for q in Path('/proc').iterdir():
 if not q.name.isdigit():continue
 try:
  a=(q/'cmdline').read_bytes().split(bytes([0]))
  if len(a)>2 and a[1]==str(P/'guest-post-controller.py').encode() and a[2]==sys.argv[1].encode():ids.append(int(q.name))
 except OSError:pass
for pid in ids:os.kill(pid,15)
print('POST_WAIT_STOPPED',ids,flush=True)
subprocess.run(['python3',str(P/'guest-post-controller.py'),sys.argv[1]],check=True)
