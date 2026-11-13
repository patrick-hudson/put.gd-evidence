#!/usr/bin/env python3
"""Omit redundant nonsecret concurrency/version markers from public copies only.
Raw receipts stay on the builders. Exact B2 objectReference.fileId and artifact
SHA-256 remain in the published copies, as do comparison outcomes.
"""
import hashlib,json,pathlib,re
root=pathlib.Path('/tmp/sa1113/evidence');changes=[]
pattern=re.compile(r'("concurrencyToken"\s*:\s*)"([^"\\]*(?:\\.[^"\\]*)*)"')
for p in root.rglob('*'):
 if not p.is_file() or p.suffix not in ('.json','.jsonl'):continue
 old=p.read_bytes();text=old.decode();count=[0]
 def replace(m):
  if not m[2] or m[2]=='omitted':return m[0]
  count[0]+=1;return m[1]+'"omitted"'
 new=pattern.sub(replace,text).encode()
 if count[0]:
  p.write_bytes(new);changes.append({'file':str(p.relative_to(root)),'field':'concurrencyToken','omittedOccurrences':count[0],'originalSha256':hashlib.sha256(old).hexdigest(),'publishedSha256':hashlib.sha256(new).hexdigest()})
(root/'receipts/publication-redactions.json').write_text(json.dumps({'reason':'Redundant nonsecret file-version / digest markers matched the generic API-key scanner; no authentication values were found. Raw copies remain on builders. Exact B2 fileId and artifact SHA-256 retained.','files':changes},indent=2)+'\n')
print({'files':len(changes),'omittedFields':sum(x['omittedOccurrences'] for x in changes)})
