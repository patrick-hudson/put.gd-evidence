import hashlib,json,sys,zipfile
from pathlib import Path
root=Path.home()/'work/ocr-integration-bcb-artifacts'
label=sys.argv[1]
meta=json.loads((root/(label+'-artifact.json')).read_text())
archive=root/(label+'.zip')
actual=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()
assert meta['digest']=='sha256:'+actual,(label,'digest mismatch')
assert meta['workflow_run']['head_sha']=='bcb868f9ac5b50967976656ed306858f5d8ae72f'
output=root/label
output.mkdir()
with zipfile.ZipFile(archive) as z:
 for n in z.namelist():
  assert (output/n).resolve().is_relative_to(output.resolve()),n
 z.extractall(output)
print(label,meta['id'],actual)
