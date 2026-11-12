from pathlib import Path
import subprocess
for p in [Path('/usr/lib/firefox/omni.ja'),Path('/usr/lib/firefox/browser/omni.ja')]:
 if not p.exists():continue
 entries=subprocess.run(['unzip','-Z1',str(p)],capture_output=True,text=True).stdout.splitlines()
 for n in entries:
  if not any(x in n.lower() for x in ['termsofuse','terms-of-use','policies','firefox.js']):continue
  s=subprocess.run(['unzip','-p',str(p),n],capture_output=True,text=True).stdout
  print(p,n)
  for line in s.splitlines():
   if any(x in line.lower() for x in ['termsofuse','skipterms','accepteddate']):print(line[:400])
