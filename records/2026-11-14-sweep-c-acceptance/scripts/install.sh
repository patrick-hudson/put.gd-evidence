#!/bin/bash
set -eu
cd /home/patrick/work/sc1114
sudo -n apt-get -y install /home/patrick/work/sb1114/artifacts/ubuntu24.04/putgd_26.1113.4927~dev+gdd7e9c4b18b7_amd64.deb >install.log 2>&1
python3 - <<'PY'
from pathlib import Path
import hashlib,json,shutil,subprocess,os
root=Path.cwd();target=root/'native-bin';target.mkdir(mode=0o700);copies=[]
for p in Path('/usr/bin').glob('putgd*'):
 if p.is_file():
  q=target/p.name;shutil.copy2(p,q);h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==hashlib.sha256(q.read_bytes()).hexdigest();copies.append({'installed':str(p),'copy':str(q),'sha256':h})
appdir=Path('/home/patrick/work/sb1114/analyzer/squashfs-root')
native=json.loads(subprocess.check_output(['/usr/bin/putgd','--version-json'],text=True));helper=json.loads(subprocess.check_output([str(appdir/'usr/bin/putgd-record'),'--version-json'],env=dict(os.environ,APPDIR=str(appdir)),text=True));assert native==helper;assert native['gitTree']=='e12d7610bec4319749a5b55b5411ce3f2b7318c2'
(target/'putgd-record').rename(target/'putgd-record-native');q=target/'putgd-record';q.write_text('#!/bin/sh\nexport APPDIR='+str(appdir)+'\nexec '+str(appdir/'usr/bin/putgd-record')+' "$@"\n');q.chmod(0o700)
(root/'native-appimage-helper.json').write_text(json.dumps({'native':native,'helper':helper,'copies':copies},indent=2))
shutil.copy2('/home/patrick/work/sb1114/record_acceptance.py',root/'record_acceptance.py')
(root/'tools').symlink_to('/home/patrick/work/sb1114/tools',target_is_directory=True)
PY
