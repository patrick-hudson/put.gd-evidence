from tools.lab import proton_lab as p,lab
from pathlib import Path
import json,shlex,os
from common import RUN,shell
class Stock(p.Guest):
 def place_brokers(self,source):
  shell('mkdir -m 700 /dev/shm/oc-bridge-libs; p=$(pgrep -x putgd | head -1); d=$(dirname "$(readlink /proc/$p/exe)"); cp -L "$d/../lib/libqt6keychain.so.1" /dev/shm/oc-bridge-libs/libqt6keychain.so.1')
  self.directory='/home/lab/oc-proton-bridge';lab.ssh(self.run,'mkdir -m 700 '+self.directory)
  for name,path in p.brokers(source).items():
   dest=self.directory+'/'+Path(path).name+'.bin';lab.put(self.run,path,dest);lab.ssh(self.run,'chmod 700 '+dest)
  text='''#!/bin/sh
export LD_LIBRARY_PATH=/dev/shm/oc-bridge-libs
exec "$(dirname "$0")/putgd-lab-secret-bridge.bin" "$@"
'''
  lab.ssh(self.run,'cat > '+self.directory+'/putgd-lab-secret-bridge <<\'WRAP\'\n'+text+'WRAP\nchmod 700 '+self.directory+'/putgd-lab-secret-bridge\nmv '+self.directory+'/putgd-lab-proton-secrets.bin '+self.directory+'/putgd-lab-proton-secrets')
  return dict(qt=self.directory+'/putgd-lab-secret-bridge',proton=self.directory+'/putgd-lab-proton-secrets')
 def prepare_keyring(self):
  # Read-only: keep Omarchy's actual default collection, no lab collection/alias.
  v=shell('busctl --user get-property org.freedesktop.secrets /org/freedesktop/secrets/collection/Default_5fkeyring org.freedesktop.Secret.Collection Locked')
  assert v.strip()=='b false';return dict(provider='gnome-keyring',collection='Default_keyring',stock=True)
 def stop_app(self):
  super().stop_app()
 def remove_brokers(self):
  lab.ssh(self.run,'rm -- /dev/shm/oc-bridge-libs/libqt6keychain.so.1; rmdir /dev/shm/oc-bridge-libs')
  lab.ssh(self.run,'rm -- '+self.directory+'/putgd-lab-secret-bridge '+self.directory+'/putgd-lab-secret-bridge.bin '+self.directory+'/putgd-lab-proton-secrets\nrmdir '+self.directory)
if __name__=='__main__':
 layout=p.Layout();layout.prepare()
 r=p.lend(layout,str(RUN),'oc-credentials','oc-credentials','stock Omarchy credential validation',['python3','proton_flow.py'],guest_factory=Stock,guest_reference=json.loads(Path('/home/patrick/putgd-lab/proton/receipts/2026-11-08T23-57-30Z-o1/lend.json').read_text())['reference'])
 print(json.dumps(r))
