"""Install only the supplied checksum-verified published pacman package."""
import hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab
run=Path(sys.argv[1]).resolve();package=Path(sys.argv[2]).resolve();out=Path(sys.argv[3]).resolve();out.mkdir(mode=0o700,exist_ok=True,parents=True)
lab.verify_owned_guest(run)
protected='hyprland omarchy quickshell xdg-desktop-portal xdg-desktop-portal-hyprland pipewire mesa'
before=lab.ssh(run,'pacman -Q '+protected)
lab.put(run,package,'putgd-nightly.pkg.tar.zst')
transaction=lab.ssh(run,'sudo -n pacman -U --noconfirm --ignore hyprland,omarchy,quickshell,xdg-desktop-portal,xdg-desktop-portal-hyprland,pipewire,mesa "$HOME/putgd-nightly.pkg.tar.zst"',timeout=900)
(out/'arch-install.txt').write_text(transaction)
after=lab.ssh(run,'pacman -Q '+protected)
(out/'desktop-before.txt').write_text(before);(out/'desktop-after.txt').write_text(after)
assert before==after,'Arch package changed a protected desktop component'
members=subprocess.check_output(['tar','--zstd','-tf',str(package)],text=True).splitlines()
expected={}
for member in members:
 p=Path(member)
 if p.parent.as_posix()=='usr/bin' and p.name.startswith('putgd'):
  raw=subprocess.check_output(['tar','--zstd','-xOf',str(package),member])
  expected['/'+p.as_posix()]=hashlib.sha256(raw).hexdigest()
assert '/usr/bin/putgd' in expected
actual={}
for path,digest in expected.items():
 value=lab.ssh(run,'sha256sum '+path).split()[0];assert value==digest
 actual[path]=value
receipt=dict(format='arch',filename=package.name,sha256=lab.hash_file(package),installedBinarySha256=actual)
lab.write_json(run/'package.json',receipt);lab.write_json(out/'arch-install.json',receipt)
print(json.dumps(receipt))
