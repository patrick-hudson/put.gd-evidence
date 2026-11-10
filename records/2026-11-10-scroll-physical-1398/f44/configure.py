import json,subprocess
from pathlib import Path
p=Path('/tmp/sp1398');env=json.loads((p/'env.json').read_text())
def rpc(m,x={}):
 o=json.loads(subprocess.check_output(['putgd-cli','--socket',str(p/'runtime/putgd/session.sock'),m,json.dumps(x)],env=env,text=True));assert o['ok'],o;return o['result']
s=rpc('settings.get');d=s['document'];d['archive'].update(keepUploads=True,root=str(p/'archive'));print(rpc('settings.save',{'document':d,'expectedRevision':s['metadata']['observedRevision']}));print(rpc('scroll.capabilities'))
