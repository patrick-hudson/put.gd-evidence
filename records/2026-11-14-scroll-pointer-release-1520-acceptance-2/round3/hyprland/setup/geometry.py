import json,subprocess,os
from types import SimpleNamespace
def output():
 if any(x in os.environ.get("XDG_CURRENT_DESKTOP","") for x in ["GNOME","KDE"]):
  from trial import Rfb
  return Rfb(5901 if "GNOME" in os.environ.get("XDG_CURRENT_DESKTOP","") else 5900)
 if 'Hyprland' in os.environ.get('XDG_CURRENT_DESKTOP',''):
  v=json.loads(subprocess.check_output(['hyprctl','monitors','-j'],text=True))[0];return SimpleNamespace(width=v['width'],height=v['height'],sock=None)
 displays=json.loads(subprocess.check_output(['wlr-randr','--json'],text=True));active=[d for d in displays if d.get('enabled')]
 if len(active)!=1:raise RuntimeError('one active output required for this local-input driver')
 mode=next(m for m in active[0]['modes'] if m.get('current'))
 return SimpleNamespace(width=mode['width'],height=mode['height'],sock=None)
