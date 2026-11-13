import datetime,hashlib,json,re
from pathlib import Path
r=Path.home()/'work/ocr-integration-bcb-artifacts'
commit='bcb868f9ac5b50967976656ed306858f5d8ae72f'
receipt={'schemaVersion':1,'run':43380438975,'commit':commit,'host':'k72','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{},'scope':'Fresh required-dependencies-only install per native package kind; no GUI or resident session started'}
for kind,label in [('deb','integration-ubuntu24.04'),('rpm','integration-fedora44'),('arch','integration-arch')]:
 identity=json.loads((r/(kind+'-helper-identity.json')).read_text())
 assert identity['gitCommit']==commit
 log=(r/(kind+'-clean-install.log')).read_text()
 assert 'PASS:' in log
 data=(r/(kind+'-english-data.sha256')).read_text().strip()
 meta=json.loads((r/(label+'-artifact.json')).read_text())
 package=next(p for p in (r/label).iterdir() if p.name.endswith(('.deb','.rpm','.pkg.tar.zst')))
 sizes={}
 if kind=='deb':
  for line in (r/'deb-ocr-package-sizes.tsv').read_text().splitlines():
   status,name,version,size=line.split('\t'); assert status.startswith('ii'); sizes[name]={'version':version,'installedBytes':int(size)*1024}
 elif kind=='rpm':
  for line in (r/'rpm-ocr-package-sizes.tsv').read_text().splitlines():
   name,version,size=line.split('\t'); sizes[name]={'version':version,'installedBytes':int(size)}
 else:
  for p in (r/'arch-installed-package-db').glob('*/desc'):
   fields={}
   for chunk in p.read_text().strip().split('\n\n'):
    lines=chunk.splitlines()
    fields[lines[0].strip('%')]=lines[1:]
   name=fields['NAME'][0]
   if name in ('tesseract','tesseract-data-eng','zxing-cpp','leptonica','zint'):
    sizes[name]={'version':fields['VERSION'][0],'installedBytes':int(fields['SIZE'][0])}
 assert len(sizes)==(5 if kind=='arch' else 4)
 if kind in ('deb','rpm'):
  def packages(path):
   result={}
   for line in path.read_text().splitlines():
    name,version,size=line.split('\t'); result[name]={'version':version,'bytes':int(size)*(1024 if kind=='deb' else 1)}
   return result
  before=packages(r/(kind+'-clean-before.tsv')); after=packages(r/(kind+'-clean-after.tsv'))
 else:
  after={}
  for p in (r/'arch-installed-package-db').glob('*/desc'):
   fields={}
   for chunk in p.read_text().strip().split('\n\n'):
    lines=chunk.splitlines(); fields[lines[0].strip('%')]=lines[1:]
   after[fields['NAME'][0]]={'version':fields['VERSION'][0],'bytes':int(fields['SIZE'][0])}
  before={}
  for line in (r/'arch-clean-before-install.txt').read_text().splitlines():
   name,version=line.split(); assert after[name]['version']==version
   before[name]=after[name]
 full_added=sum(p['bytes'] for p in after.values())-sum(p['bytes'] for p in before.values())
 (r/(kind+'-all-installed-sizes.json')).write_text(json.dumps({'before':before,'after':after},indent=2)+'\n')
 receipt['checks'][kind]={'totalInstalledSizeIncreaseBytes':full_added,'installedSizeBasis':'package-manager uncompressed size metadata; includes putgd and all newly required packages; excludes package download caches','artifactId':meta['id'],'package':package.name,'packageSha256':hashlib.file_digest(package.open('rb'),'sha256').hexdigest(),'identity':identity,'optionalDependencies':False,'startedWithoutOcrPackages':True,'engineAndEnglishPackages':sizes,'engineAndEnglishInstalledBytes':sum(s['installedBytes'] for s in sizes.values()),'englishData':data,'helperLdd':(r/(kind+'-helper-ldd.txt')).read_text(),'logSha256':hashlib.file_digest((r/(kind+'-clean-install.log')).open('rb'),'sha256').hexdigest()}
(r/'clean-install-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:{'installedBytes':v['engineAndEnglishInstalledBytes'],'packages':v['engineAndEnglishPackages']} for k,v in receipt['checks'].items()},indent=2))
