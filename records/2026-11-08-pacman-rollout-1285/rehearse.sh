#!/bin/bash
set -eu
umask 077
export AWS_CONFIG_FILE="$HOME/.config/putgd-signer/aws-config"
export AWS_SHARED_CREDENTIALS_FILE="$HOME/.config/putgd-signer/aws-credentials"
export AWS_SDK_LOAD_CONFIG=1
export GNUPGHOME="$HOME/.local/share/putgd-signer/gnupg"
export PYTHONDONTWRITEBYTECODE=1
python3 - <<'PY'
import sys,pathlib,json,os
root=pathlib.Path.home()/'work/rollout1285'
sys.path.insert(0,str(pathlib.Path.home()/'putgd-signer/src/tools/releases'))
import pkgrepo
gh=pkgrepo.GitHub(pkgrepo.REPOSITORY)
r=next(r for r in gh.releases() if r['tag_name']=='v26.1108.4139-nightly')
i=pkgrepo.verify_release(r,gh,root/'verified-release')
(root/'verified-inputs.json').write_text(json.dumps({'tag':i['tag'],'commit':i['commit'],'checks':i['checks'],'packages':{k:{kk:vv for kk,vv in v.items() if kk!='path'} for k,v in i['packages'].items()}},indent=2))
a=root/'lab-assets';a.mkdir(mode=0o700)
for p in i['packages'].values():os.link(p['path'],a/p['name'])
(a/'SHA256SUMS').write_text(''.join(p['sha256']+'  '+p['name']+'\n' for p in i['packages'].values()))
print('Verified release tag, receipts, hashes and package fields; staged five native lab inputs.',flush=True)
PY
python3 "$HOME/putgd-signer/src/tools/releases/pkgrepo.py" publish-local --tag v26.1108.4139-nightly --assets "$HOME/work/rollout1285/lab-assets"
