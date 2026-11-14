import os,pathlib
for p in pathlib.Path('/proc').iterdir():
 try:
  if (p/'comm').read_text().strip()=='quickshell':
   e=dict(v.split('=',1) for v in (p/'environ').read_bytes().decode().split('\0') if '=' in v)
   if 'OMARCHY_PATH' in e:break
 except (OSError,UnicodeError):pass
assert e.get('OMARCHY_PATH')=='/usr/share/omarchy'
os.environ.update(e)
os.execv('/usr/bin/omarchy',['omarchy','update'])
