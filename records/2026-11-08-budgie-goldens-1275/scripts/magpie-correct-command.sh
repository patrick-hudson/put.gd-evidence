python3 - <<'PY'
from pathlib import Path
import time
out=Path('/tmp/magpie-a2');config=Path.home()/'.config/budgie-desktop/magpierc'
(out/'magpierc-first-format').write_bytes(config.read_bytes())
# Pinned config.cpp reads only entry[2] and splits spaces; it ignores further comma items.
config.write_text('[Keybinds]\n'+''.join('probe'+k+'=Ctrl+Shift+'+k+',A1275 probe,/usr/bin/touch /tmp/magpie-a-'+k+'\n' for k in ['F9','1','2','3']))
time.sleep(3)
(out/'magpierc-corrected').write_bytes(config.read_bytes())
print(config.read_text())
PY
