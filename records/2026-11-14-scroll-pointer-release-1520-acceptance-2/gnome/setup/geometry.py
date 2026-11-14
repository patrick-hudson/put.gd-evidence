import json,subprocess,os
from types import SimpleNamespace
def output():
 if "GNOME" in os.environ.get("XDG_CURRENT_DESKTOP",""):
  from trial import Rfb
  return Rfb(5901)
 displays=json.loads(subprocess.check_output(['wlr-randr','--json'],text=True));active=[d for d in displays if d.get('enabled')]
 if len(active)!=1:raise RuntimeError('one active output required for this local-input driver')
 mode=next(m for m in active[0]['modes'] if m.get('current'))
 return SimpleNamespace(width=mode['width'],height=mode['height'],sock=None)
