import json,subprocess,time,os
from pathlib import Path
import rfb
p=Path('/tmp/sp1398');env=json.loads((p/'env.json').read_text());port=5901 if os.uname().nodename=='fedora' else 5900
# Fixture is explicitly opened by this test; keyboard/drag are the user trigger,
# not product scroll injection. Never send input outside the owned test fixture.
def rpc(m,x={}):
 o=json.loads(subprocess.check_output(['putgd-cli','--socket',str(p/'runtime/putgd/session.sock'),m,json.dumps(x)],env=env,text=True));assert o['ok'],o;return o['result']
s=rpc('settings.get');(p/'pre-shortcut.json').write_text(json.dumps(s));rpc('settings.patch',{'patch':{'actions':{'scroll':{'shortcut':'Ctrl+Alt+F7'}}},'expectedRevision':s['metadata']['observedRevision']})
subprocess.run(['python3',str(p/'start_fixture.py')]);time.sleep(9)
v=rfb.RFB(port);v.screenshot(p/'user-before.png');v.key('ctrl','alt','f7');time.sleep(1);v.screenshot(p/'user-selector.png');v.drag(100,100,1060,700)
for i in range(14):v.screenshot(p/('user-capture-%02d.png'%i));time.sleep(.4)
(p/'user-history.json').write_text(json.dumps(rpc('history.list',{'limit':200}),indent=2))
s=rpc('settings.get');rpc('settings.patch',{'patch':{'actions':{'scroll':{'shortcut':''}}},'expectedRevision':s['metadata']['observedRevision']})
