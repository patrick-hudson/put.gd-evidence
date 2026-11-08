import sys,json,os,re,uuid,ast,types,shlex,subprocess
from pathlib import Path
root=Path.home()/'work/b1275/lab';sys.path.insert(0,str(root))
from tools.lab import provision_live_credentials as original
# Budgie session discovery is already supported by lab.py; this older credential
# helper's three-desktop allowlist requires the same addition in this scratch run.
bridge=types.ModuleType('b4_bridge');bridge.__file__=str(root/'tools/lab/provision_live_credentials.py')
exec(compile(Path(bridge.__file__).read_text().replace("('cinnamon', 'gnome-shell', 'plasmashell')","('cinnamon', 'gnome-shell', 'plasmashell', 'budgie-panel')"),bridge.__file__,'exec'),bridge.__dict__)
source=ast.parse((root/'tools/lab/surface_driver/fixtures/live_outcomes.py').read_text());node=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='key_set_two');exec(compile(ast.Module(body=[node],type_ignores=[]),'key_set_two','exec'))
run=str(root/'work/lab-runs/u26c');out=Path.home()/'work/b1275/b4';broker='/home/lab/b4-bridge/putgd-lab-secret-bridge'
def cli(method,args={}):
    raw=bridge.lab.ssh(run,'bash -c '+shlex.quote('source ~/genv.sh; putgd-cli '+shlex.quote(method)+' '+shlex.quote(json.dumps(args))),timeout=120)
    value=json.loads(raw);(out/(method.replace('.','-')+'-last.json')).write_text(json.dumps(value,indent=2));assert value['ok'],value['error'];return value['result']
if sys.argv[1]=='setup':
    selected=key_set_two(original.read_private_credentials(Path.home()/'Documents/creds.txt'))
    assert selected['settings']['bucket']=='put.gd'
    receipt=out/'live-receipt.json'
    if receipt.exists():
        state=json.loads(receipt.read_text());assert state['state']=='import_confirmed';ref=state['credentialReference']['reference'];prefix='acceptance/b1275-'+uuid.uuid4().hex[:12]+'/'
    else:
        ref='putgd-lab-'+str(uuid.uuid4());prefix='acceptance/b1275-'+uuid.uuid4().hex[:12]+'/'
        state=bridge._receipt_value('s3','guest',run,ref,'one_time','import_pending',True);bridge._create_receipt(receipt,state)
        bridge.guest_call(run,broker,'s3',dict(op='import',reference=ref,credentials=selected['credentials']))
        bridge._update_receipt(receipt,state,state='import_confirmed')
    settings=json.loads((Path.home()/'work/put.gd/config/development.example.json').read_text())['profiles'][0]['settings'];region=selected['settings']['region'];settings.update(bucket='put.gd',region=region,endpoint='https://s3.'+region+'.amazonaws.com',objectPrefix=prefix,publicUrlBase='https://put.gd',aclMode='public-read',addressing='auto')
    meta=dict(reference=ref,prefix=prefix,region=region);(out/'live.json').write_text(json.dumps(meta))
    current=cli('settings.get');cli('settings.patch',dict(expectedRevision=current['metadata']['acceptedRevision'],patch=dict(profiles=[dict(id='b4-live',label='B4 isolated live',provider='s3',settings=settings,credentials=dict(mode='keychain',reference=ref))],actions={'region':dict(destination='upload',profileId='b4-live',publicationMode='share')})))
    print('key set 2 imported; profile configured; prefix',prefix)
elif sys.argv[1]=='call':
    print(json.dumps(cli(sys.argv[2],json.loads(sys.argv[3]) if len(sys.argv)>3 else {})))
elif sys.argv[1]=='list':
    selected=key_set_two(original.read_private_credentials(Path.home()/'Documents/creds.txt'));m=json.loads((out/'live.json').read_text());keys=selected['credentials'];env=os.environ.copy();env.update(AWS_ACCESS_KEY_ID=keys['accessKey'],AWS_SECRET_ACCESS_KEY=keys['secretKey'],AWS_DEFAULT_REGION=m['region'],AWS_PAGER='')
    r=subprocess.run(['aws','s3api','list-objects-v2','--bucket','put.gd','--prefix',m['prefix'],'--no-paginate','--output','json'],env=env,capture_output=True);assert r.returncode==0,'read-only prefix listing failed';data=json.loads(r.stdout);(out/'prefix-list.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
elif sys.argv[1]=='cleanup-key':
    m=json.loads((out/'live.json').read_text());bridge.cleanup(dict(op='cleanup',provider='s3',run=run,guestBroker=broker,reference=m['reference'],receipt=str(out/'live-receipt.json')));print('keychain reference deleted')
