from tools.lab import lab
from tools.lab.provision_live_credentials import read_private_credentials
from tools.lab.surface_driver.fixtures.live_outcomes import key_set_two
from pathlib import Path
import json,base64
r=Path('work/lab-runs/o1')
v=key_set_two(read_private_credentials(Path.home()/'Documents/creds.txt'))['credentials']
raw=lab.guest_session(r,'secret-tool lookup user putgd/oc-acceptance server putgd')
x=json.loads(base64.b64decode(raw))
print({k:x[k]==v[k] for k in v})
print(lab.ssh(r,"python3 - <<'PY2'\nimport json\nfrom pathlib import Path\np=json.loads((Path.home()/'.config/putgd/config.json').read_text())['profiles'][0];print(p['settings'])\nPY2"))
