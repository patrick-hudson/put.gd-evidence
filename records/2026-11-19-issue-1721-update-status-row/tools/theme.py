import sys, os, json
sys.path.insert(0, os.path.expanduser('~/work/w1721/drv'))
import drv_lib
cli='/var/home/patrick/work/w1721/tagged/build/release/putgd-cli'
d=json.loads(drv_lib.cli('after', cli, 'settings.get'))['result']
print('appearance before', d['document']['preferences'].get('appearance'))
r=drv_lib.cli('after', cli, 'settings.patch', {'patch':{'preferences':{'appearance':{'theme':'dark'}}},'expectedRevision':d['metadata']['observedRevision']})
print(r[:300])
