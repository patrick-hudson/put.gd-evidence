from pathlib import Path
import shutil,json
p=Path('/home/lab/firefox-fixture');shutil.copytree('/usr/lib/firefox',p)
d=p/'distribution';d.mkdir(exist_ok=True);f=d/'policies.json';assert not f.exists();f.write_text(json.dumps({'policies':{'SkipTermsOfUse':True}}))
print('Private distro Firefox copy ready with SkipTermsOfUse')
