import json,subprocess
from pathlib import Path
p=Path('/home/patrick/work/pcn');env=json.loads((p/'env.json').read_text())
def rpc(m,x={}):
 o=json.loads(subprocess.check_output(['putgd-cli','--socket',str(p/'r/putgd/session.sock'),m,json.dumps(x)],env=env,text=True));assert o['ok'],o;return o['result']
r=subprocess.Popen(['python3',str(p/'receiver.py')],stdout=open(p/'receiver.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(p/'receiver.pid').write_text(str(r.pid))
(p/'loopback.sxcu').write_text(json.dumps({'Name':'Synthetic local scroll acceptance','DestinationType':'ImageUploader','RequestMethod':'POST','RequestURL':'http://127.0.0.1:19399/upload','Body':'MultipartFormData','FileFormName':'file','URL':'{json:url}'}))
s=rpc('settings.get');print(rpc('settings.importUploader',{'path':str(p/'loopback.sxcu'),'profileId':'scroll-local','credentialMode':'session','allowInsecureHttp':True,'expectedRevision':s['metadata']['observedRevision']}))
s=rpc('settings.get');print(rpc('settings.patch',{'patch':{'actions':{'scroll':{'destination':'upload','profileId':'scroll-local'}}},'expectedRevision':s['metadata']['observedRevision']}))
