from tools.lab.provision_live_credentials import read_private_credentials
from tools.lab.surface_driver.fixtures.live_outcomes import key_set_two
from pathlib import Path
import subprocess,os,json
v=key_set_two(read_private_credentials(Path.home()/'Documents/creds.txt'));c=v['credentials'];env=dict(os.environ,AWS_ACCESS_KEY_ID=c['accessKey'],AWS_SECRET_ACCESS_KEY=c['secretKey'],AWS_DEFAULT_REGION=v['settings']['region'],AWS_PAGER='')
for op in ['list-objects-v2','list-multipart-uploads']:
 p=subprocess.run(['aws','s3api',op,'--bucket','put.gd','--prefix','acceptance/oc-20261108/','--output','json'],env=env,capture_output=True,text=True);assert p.returncode==0,'s3_listing_failed';r=json.loads(p.stdout);print(op,dict(count=r.get('KeyCount',len(r.get('Uploads',[])))))
