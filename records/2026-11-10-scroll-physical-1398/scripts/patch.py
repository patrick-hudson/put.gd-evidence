import json,subprocess,sys
from pathlib import Path
p=Path('/tmp/sp1398');e=json.loads((p/'env.json').read_text())
def rpc(m,x={}):
 o=json.loads(subprocess.check_output(['putgd-cli','--socket',str(p/'runtime/putgd/session.sock'),m,json.dumps(x)],env=e,text=True));assert o['ok'],o;return o['result']
s=rpc('settings.get');print(rpc('settings.patch',{'patch':json.loads(sys.argv[1]),'expectedRevision':s['metadata']['observedRevision']}))
