import os,select,subprocess,pathlib
base=pathlib.Path.home()/'work/f44-editor-ab-1247'
for label,kind in [('c2b','candidate'),('n2','nightly')]:
 import socket,time
 for _ in range(90):
  try:
   for port in [22446,5946]:
    with socket.socket() as sock:sock.bind(('127.0.0.1',port))
   break
  except OSError:time.sleep(1)
 with (base/(label+'.log')).open('xb') as log:
  subprocess.run(['python3','-u',str(base/'run.py'),label,kind],stdout=log,stderr=log,check=True)
print('four rows complete',flush=True)
