from pathlib import Path
import re,json,gzip,hashlib,shutil
B=Path(__file__).parent;G=B/'2026-11-12-scroll-accept2-1398';pat=re.compile(rb'("concurrencyToken"\s*:\s*)"(?:\\.|[^"\\])*"');changes=[]
for p in list(G.rglob('*')):
 if not p.is_file() or p.suffix in ['.png','.jpg','.webp','.gif','.multipart']:continue
 old=p.read_bytes();raw=gzip.decompress(old) if p.suffix=='.gz' else old
 new,n=pat.subn(lambda m:m.group(1)+b'"[redacted synthetic receipt nonce]"',raw)
 if not n or new==raw:continue
 encoded=gzip.compress(new,compresslevel=9,mtime=0) if p.suffix=='.gz' else new
 p.write_bytes(encoded);changes.append({'path':str(p.relative_to(G)),'fieldsReplaced':n,'originalSha256':hashlib.sha256(old).hexdigest(),'publicSha256':hashlib.sha256(encoded).hexdigest(),'originalUncompressedSha256':hashlib.sha256(raw).hexdigest(),'publicUncompressedSha256':hashlib.sha256(new).hexdigest()})
index=json.loads((G/'compressed-logs.json').read_text());by={x['path']:x for x in changes}
for x in index:
 if x['compressed'] not in by:continue
 p=G/x['compressed'];c=by[x['compressed']];raw=gzip.decompress(p.read_bytes());x['privateOriginalSha256']=x['originalSha256'];x['privateCompressedSha256']=x['compressedSha256'];x['originalSha256']=hashlib.sha256(raw).hexdigest();x['compressedSha256']=hashlib.sha256(p.read_bytes()).hexdigest();x['originalBytes']=len(raw);x['sanitized']='Only synthetic receipt concurrencyToken values redacted. Original logs remain in private archives.'
(G/'compressed-logs.json').write_text(json.dumps(index,indent=2))
(G/'log-sanitization.json').write_text(json.dumps({'reason':'Evidence CI generic-api-key flags matched 36-character custom-http receipt concurrencyToken values equal to objectReference.nonce. These synthetic loopback upload receipt guards are not credentials (HttpWorkerMain.cpp receipt construction). Values are redacted from public logs; original logs remain in the checksum-verified private archives. Capture PNGs, operation IDs, results, timing and verifier pixels are unchanged. Original cleanup/export manifest hashes refer to the private originals; this file maps sanitized public bytes.','initialEvidenceCommit':'09ab6d525ac49cf69ef5d376820bd527f8df0327','ciRun':43146372709,'all2182FlaggedLinesContainedThisField':True,'changes':changes},indent=2))
p=G/'README.md';s=p.read_text();s+='\nPublic JSON/RPC logs redact synthetic custom-HTTP receipt `concurrencyToken` markers after the evidence CI generic-key rule flagged them. All inspected nonempty markers were 36-character values equal to their receipt nonce; they are not upload credentials. PNGs and operation IDs are unchanged. [log-sanitization.json](log-sanitization.json) maps private original hashes to public hashes; original export/cleanup manifests describe the private originals. The compressed-log restore index hashes describe the redacted public logs.\n';p.write_text(s)
shutil.copyfile(Path(__file__),G/'drivers'/Path(__file__).name)
manifest={str(p.relative_to(G)):hashlib.sha256(p.read_bytes()).hexdigest() for p in G.rglob('*') if p.is_file() and p.name!='SHA256SUMS.json'};(G/'SHA256SUMS.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n');print('sanitized',len(changes),'files',sum(x['fieldsReplaced'] for x in changes),'fields')
