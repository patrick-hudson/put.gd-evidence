from pathlib import Path
import datetime,hashlib,json,tarfile
r=Path.home()/'work/ocr-integration-bcb-artifacts'
commit='bcb868f9ac5b50967976656ed306858f5d8ae72f'
run=43380438975
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
# Bind every SBOM to the independently downloaded exact installer.
receipts=json.loads((r/'integration-sboms/sbom-receipts.json').read_text())['sboms']
labels={'appimage':'integration-appimage','archlinux':'integration-arch','fedora44':'integration-fedora44','debian13':'integration-debian13','ubuntu24.04':'integration-ubuntu24.04','ubuntu26.04':'integration-ubuntu26.04'}
packages={}
for label,folder in labels.items():
 s=receipts[label]; package=r/folder/s['package']; cdx=r/'integration-sboms'/s['file']
 assert sha(package)==s['packageSha256'];assert sha(cdx)==s['sha256']
 identity=json.loads((r/folder/'build-info.json').read_text());assert identity['gitCommit']==commit
 d=json.loads(cdx.read_text()); assert d['metadata']['component']['version']==identity['version']
 assert any(c['name']=='qrcodegen' and c['version']=='1.8.0' for c in d['components'])
 if label=='appimage':
  for name,version in [('tesseract','5.5.4'),('leptonica','1.87.0'),('zxing-cpp','3.1.1'),('tessdata_fast','874164186573'),('libzueci','1.0.1')]:
   assert any(c['name']==name and c['version']==version for c in d['components']),(name,version)
 packages[label]={'file':package.name,'bytes':package.stat().st_size,'sha256':s['packageSha256'],'sbom':s['file'],'sbomSha256':s['sha256'],'components':s['components'],'identity':identity}
# Verify the actual exported archive, each included member, and CI's real compile receipt.
f=r/'integration-ubuntu24.04'; source=json.loads((f/'source-archive.json').read_text()); result=json.loads((f/'source-build-results.json').read_text()); params=json.loads((f/'source-build-parameters.json').read_text())
assert source['identity']['gitCommit']==commit
archive=f/source['artifact']['file'];assert sha(archive)==source['artifact']['sha256'] and archive.stat().st_size==source['artifact']['bytes']
assert result['passed'] and result['archive']==source['artifact'] and params['archive']==source['artifact']
assert result['compiledBuild']['gitCommit']==commit and result['compiledBuild']['sourceProvenance']=='supplied'
assert 'putgd-ocr' in result['identityMatchedPrograms']
assert params['bundleProton'] and result['rebuiltProton']['sha256']==result['rebuiltProton']['bundledSha256']
assert not any('-n' in c for c in result['commands'])
required=['src/core/qrcodegen/qrcodegen.cpp','src/core/qrcodegen/qrcodegen.hpp','cmake/dependency-lock.json','cmake/Ocr.cmake','tools/verify_dependencies.py','tools/releases/provision-appimage.py','tools/releases/build-appimage.sh','tools/releases/portable_appimage.py','tools/releases/appimage_complete_sources.py','tools/releases/appimage_notices.py','tools/maintenance/refresh_pins.py','tools/releases/provision-sdk.sh','packaging/appimage/tools.lock.json','packaging/appimage/components.json','packaging/appimage/BSD-3-Clause.txt','packaging/linux/qrcodegen-LICENSE','docs/release/build.md']
selected={}
with tarfile.open(archive,'r:gz') as t:
 for member in source['members']:
  data=t.extractfile(source['archiveRoot']+'/'+member['path']).read()
  assert len(data)==member['bytes'] and hashlib.sha256(data).hexdigest()==member['sha256'],member['path']
  if member['path'] in required:selected[member['path']]=member['sha256']
assert set(selected)==set(required),set(required)-set(selected)
sourcecheck={'run':run,'commit':commit,'archive':source['artifact'],'allArchiveMembersVerified':len(source['members']),'requiredPackagingAndVendoredInputs':selected,'actualProductionRebuild':result,'parameters':params,'scope':'Real CI extracted-source production build with OCR ON and bundled Proton; no application/desktop acceptance'}
(r/'source-rebuild-receipt.json').write_text(json.dumps(sourcecheck,indent=2)+'\n')
baseline=json.loads((Path.home()/'work/ocr-pkg-1438-artifacts/nightly-head-baseline.json').read_text())
size={'run':run,'commit':commit,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline':baseline,'integrationAppImage':packages['appimage'],'addedBytes':packages['appimage']['bytes']-baseline['appimage']['bytes'],'targetBytes':12000000,'packages':packages}
assert size['addedBytes']<size['targetBytes']
(r/'size-and-package-binding.json').write_text(json.dumps(size,indent=2)+'\n')
print(json.dumps({'appimageBytes':packages['appimage']['bytes'],'addedBytes':size['addedBytes'],'sourceArchive':source['artifact'],'sourceBuildSeconds':result['wallSeconds'],'identityPrograms':result['identityMatchedPrograms']},indent=2))
