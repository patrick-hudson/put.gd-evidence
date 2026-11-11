from control import *
import hashlib
p=BASE/'artifacts';files={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()};(BASE/'artifact-sha256.json').write_text(json.dumps(files,indent=2))
for h,tag in [('m74','ubuntu24.04'),('f44','fedora44'),('d69','debian13')]:
 f=next((p/('release-native-'+tag)).glob('*.rpm' if h=='f44' else '*.deb'));put(h,f,'/home/patrick/work/pcn/'+f.name)
f=next((p/'release-appimage').glob('*.AppImage'));put('d69',f,'/home/patrick/work/scn/ci.AppImage')
