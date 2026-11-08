import json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import provision_live_credentials as bridge,nightly_desktops as n
from tools.lab.surface_driver.fixtures.live_outcomes import key_set_two
selected=key_set_two(bridge.read_private_credentials(Path.home()/'Documents/creds.txt'))
env={k:v for k,v in os.environ.items() if not k.startswith('AWS_')}
env.update(AWS_ACCESS_KEY_ID=selected['credentials']['accessKey'],AWS_SECRET_ACCESS_KEY=selected['credentials']['secretKey'],AWS_DEFAULT_REGION=selected['settings']['region'],AWS_PAGER='',AWS_MAX_ATTEMPTS='2')
proofs=[]
for p in sorted(Path('work/np/u24-recovery').glob('s3_region_upload-[12].json')):
 v=json.loads(p.read_text());assert v['complete'] and v['remoteStatus'] in ('removed','already_missing')
 assert v['objectPath'].startswith(v['prefix']) and v['prefix'].startswith('acceptance/tier1-live/') and v['bucket']=='put.gd'
 r=subprocess.run(['aws','s3api','head-object','--bucket',v['bucket'],'--key',v['objectPath'],'--cli-connect-timeout','10','--cli-read-timeout','20'],env=env,capture_output=True,text=True,timeout=45)
 missing=r.returncode!=0 and '(404)' in r.stderr
 assert missing,'independent HEAD did not confirm 404'
 proofs.append(dict(historyId=v['historyId'],objectPath=v['objectPath'],head404=True))
assert len(proofs)==2
n.save(Path('work/np/u24-recovery/s3-independent-head.json'),dict(verified=True,objects=proofs))
print('2 exact recovered S3 objects independently HEAD-verified absent')
