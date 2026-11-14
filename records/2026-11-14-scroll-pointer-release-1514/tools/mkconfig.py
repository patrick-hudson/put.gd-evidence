#!/usr/bin/env python3
"""mkconfig.py TEMPLATE.json LABEL: a local-only configuration for the lab resident."""
import json, os, sys
lab = os.path.expanduser('~/work/scroll-1514-lab')
doc = json.load(open(sys.argv[1]))['result']['document']
label = sys.argv[2]
doc['profiles'] = []
for name, action in doc['actions'].items():
    if 'destination' in action:
        action['destination'] = 'local'
        action['profileId'] = None
    if 'shortcut' in action:
        action['shortcut'] = ''
    for key in ('publicationMode',):
        action.pop(key, None) if False else None
doc['archive']['keepUploads'] = True
doc['archive']['root'] = f'{lab}/{label}/out'
os.makedirs(f'{lab}/{label}/out', exist_ok=True)
path = f'{lab}/{label}/config/putgd/config.json'
os.makedirs(os.path.dirname(path), exist_ok=True)
tmp = path + '.tmp'
with open(tmp, 'w') as f:
    json.dump(doc, f, indent=1)
os.chmod(tmp, 0o600)
os.replace(tmp, path)
print(path)
