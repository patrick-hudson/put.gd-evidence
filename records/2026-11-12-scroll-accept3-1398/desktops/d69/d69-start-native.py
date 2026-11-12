from pathlib import Path
import subprocess,json,sys
P=Path('/home/patrick/work/s3a')
subprocess.run(['python3',str(P/'install-native.py'),'d69',str(P/'debian13/putgd_26.1112.4716~dev+g0311647141ff_amd64.deb')],check=True)
with (P/'test-dependencies-install.log').open('w') as log:r=subprocess.run(['sudo','-n','apt-get','install','-y','python3-pyqt6','python3-gi','python3-gi-cairo','gir1.2-gtk-4.0','python3-pil','python3-numpy','fonts-dejavu-core','chromium'],stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0;(P/'packages-after.txt').write_bytes(subprocess.check_output(['dpkg-query','-W','-f=${binary:Package}\n']))
import pass2 as p
p.setup()
with (P/'controls7.console').open('w') as log:subprocess.run(['python3',str(P/'controls7.py'),'ruler','text','resize','minimap'],stdout=log,stderr=subprocess.STDOUT,check=True)
subprocess.run(['python3',str(P/'native-rest.py'),'d69'],check=True)
print('NATIVE_A_DONE',flush=True)
