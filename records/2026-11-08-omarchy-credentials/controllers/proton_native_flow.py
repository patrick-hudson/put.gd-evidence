from common import *
from tools.lab.rfb import RFB
import os
out=Path('/home/patrick/work/oc/proton-native-result.json');ref=os.environ['PUTGD_LAB_PROTON_REFERENCE']
prior=json.loads(Path('/home/patrick/work/oc/proton-result.json').read_text())
p=dict(id='oc-proton',label='OC Proton native isolated',provider='proton-drive',credentials=dict(mode='keychain',reference=ref),settings=dict(accountRootUid='',folderUid='',shareByDefault=True,linkExpirationDays=0,sharePasswordReference=None,requestTimeoutMs=120000))
patch(dict(profiles=[p]));a=setup('inspectAccount');p['settings'].update(accountRootUid=a['accountRootUid'],folderUid=prior['folderUid'],folderName='putgd-omarchy-credentials-20261108');patch(dict(profiles=[p],actions=dict(region=dict(destination='upload',profileId='oc-proton',publicationMode='share'))));setup('testDestination');print('Native Proton account and isolated folder reused',flush=True)
r=RFB(5940);r.click(1239,65);time.sleep(.4);lab.key(RUN,['ctrl','shift','1']);time.sleep(.8);r.drag(300,250,800,550)
for _ in range(180):
 rows=call('history.list')['records'];record=next((x for x in rows if x['profileId']=='oc-proton'),None)
 if record and record.get('uploadStatus')=='uploaded':
  detail=call('history.detail',dict(id=record['id']))
  if detail['linkAvailable']:break
 time.sleep(1)
assert record and detail['linkAvailable'],'native_proton_not_shared'
hid=record['id'];summary=dict(build='76821fe6fd0319a34428cffedc3bb15caaf4f531',package='Arch',accountReused=True,folderUid='',historyId=hid,operationId=record['operationId'],upload=True,share=True);out.write_text(json.dumps(summary,indent=2));r.screenshot('/home/patrick/work/oc/proton-native-upload.png');print('Native Proton upload and share complete',flush=True)
call('ui.quit');time.sleep(1);shell('(setsid -f /usr/bin/putgd --history > /tmp/oc-proton-native-restart.log 2>&1 < /dev/null)');time.sleep(2);setup('inspectAccount');setup('testDestination');summary['restart']=True;out.write_text(json.dumps(summary,indent=2))
call('history.revokeLink',dict(id=hid))
for _ in range(180):
 d=call('history.detail',dict(id=hid))
 if d.get('shareStatus')=='revoked':break
 time.sleep(1)
assert d['shareStatus']=='revoked' and not d['linkAvailable'];summary.update(revoked=True,privateFilesRetained=1)
call('history.clear');patch(dict(profiles=[],captureDefaults=dict(destination='local',profileId=None,publicationMode='default'),actions={a:dict(destination='local',profileId=None,publicationMode='default') for a in ('region','window','desktop','clipboard','edit')}));out.write_text(json.dumps(summary,indent=2));print('Native Proton restart passed; link revoked, one additional private file; profile/history removed',flush=True)
