from tools.lab import lab
from pathlib import Path
import json,shlex,time
RUN=Path('/home/patrick/work/oc/src/work/lab-runs/o1')
def shell(body):return lab.guest_session(RUN,'unset XDG_CONFIG_HOME XDG_DATA_HOME\n'+body,timeout=180)
def call(method,params=None):
 body='p=$(pgrep -x putgd | head -1); d=$(dirname "$(readlink /proc/$p/exe)"); export LD_LIBRARY_PATH="$d/../lib"; "$d/putgd-cli" '+shlex.quote(method)+' '+shlex.quote(json.dumps(params or {}))+' 2>/dev/null || true'
 v=json.loads(shell(body));assert v['ok'],v['error']['code'];return v['result']
def patch(p):
 s=call('settings.get');return call('settings.patch',dict(patch=p,expectedRevision=s['metadata']['observedRevision']))
def setup(kind,pid='oc-proton',extra=None):
 s=call('settings.get');j=call('setup.'+kind,dict(profileId=pid,expectedRevision=s['metadata']['observedRevision'],**(extra or {})))
 for _ in range(180):
  v=call('setup.inspect',dict(id=j['setupId']))
  if v['state']!='running':break
  time.sleep(1)
 assert v['state']=='completed',v.get('error',{}).get('code');return v.get('result',{})
