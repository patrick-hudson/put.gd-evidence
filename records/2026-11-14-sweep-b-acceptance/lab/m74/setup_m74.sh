#!/bin/bash
set -eu
cd /home/patrick/work/sb1114
trap 'code=$?; printf "%s\n" "$code" >setup-m74.done' EXIT
sudo -n apt-get -y install /home/patrick/work/sb1114/artifacts/ubuntu24.04/putgd_26.1113.4927~dev+gdd7e9c4b18b7_amd64.deb > install-native.log 2>&1
mkdir -m 700 analyzer
image=$(python3 -c 'from pathlib import Path;print(next(Path("artifacts/appimage").glob("*.AppImage")).resolve())')
chmod 700 "$image"
(cd analyzer && "$image" --appimage-extract > extract.log)
python3 - <<'PY'
from pathlib import Path
import hashlib,json,os,shutil,subprocess
root=Path.cwd();target=root/'native-bin';target.mkdir(mode=0o700);manifest=[]
for p in Path('/usr/bin').glob('putgd*'):
 if p.is_file():
  dest=target/p.name;shutil.copy2(p,dest);before=hashlib.sha256(p.read_bytes()).hexdigest();assert before==hashlib.sha256(dest.read_bytes()).hexdigest();manifest.append({'installed':str(p),'copied':str(dest),'sha256':before})
appdir=root/'analyzer/squashfs-root';env=dict(os.environ,APPDIR=str(appdir));native=json.loads(subprocess.check_output(['/usr/bin/putgd','--version-json'],text=True));helper=json.loads(subprocess.check_output([str(appdir/'usr/bin/putgd-record'),'--version-json'],text=True,env=env));assert native==helper,(native,helper);assert native['gitTree']=='e12d7610bec4319749a5b55b5411ce3f2b7318c2'
(target/'putgd-record').rename(target/'putgd-record-native')
wrapper=target/'putgd-record';wrapper.write_text('#!/bin/sh\nexport APPDIR='+str(appdir)+'\nexec '+str(appdir/'usr/bin/putgd-record')+' "$@"\n');wrapper.chmod(0o700)
(root/'native-appimage-helper.json').write_text(json.dumps({'nativeBuild':native,'helperBuild':helper,'nativeCopies':manifest,'appimageRecorderSha256':hashlib.sha256((appdir/'usr/bin/putgd-record').read_bytes()).hexdigest()},indent=2))
PY
