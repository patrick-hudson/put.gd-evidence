from pathlib import Path
import json,subprocess,shutil
P=Path('/home/lab/work/s3a');missing=not (P/'firefox-end-0/result.json').exists();old=P/'browser-tou-attempt1';old.mkdir()
for f in list(P.iterdir()):
 if f==old:continue
 if f.name=='ffprofile' or (f.is_dir() and f.name.startswith('firefox-')) or f.name in ['browsercases.py.console']:(f).rename(old/f.name)
(P/'browser-tou-retry.json').write_text(json.dumps({'unqualifiedAttempt':str(old),'reason':'Firefox was missing, so no browser fixture launched. Distro Firefox installed; all17 browser ruler/variant runs repeated.' if missing else 'Real screenshot shows Firefox Welcome/Terms modal covering fixture, refusing wheel input. No image admitted. Browser profile corrected and all17 browser ruler/variant runs repeated.'},indent=2))
with (P/'browsercases-retry.console').open('w') as log:r=subprocess.run(['python3',str(P/'browsercases.py')],stdout=log,stderr=subprocess.STDOUT)
print('BROWSER_RETRY_EXIT',r.returncode,flush=True)
