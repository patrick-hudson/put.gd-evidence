python3 - <<'PY'
from pathlib import Path
p=Path.home()/'magpie-root-setup.sh'
p.write_text('''#!/bin/sh
set -eu
python3 - <<'P'
from pathlib import Path
for name in ['/usr/share/wayland-sessions/a1275-magpie.desktop','/etc/sddm.conf.d/99-z-a1275-magpie.conf']:
 p=Path(name);assert p.is_file() and not p.is_symlink();p.unlink()
P
systemctl restart sddm
''');p.chmod(0o700)
print('prepared exact-file restore to original Budgie session')
PY
