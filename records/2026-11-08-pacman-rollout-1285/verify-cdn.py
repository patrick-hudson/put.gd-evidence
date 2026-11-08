import sys,pathlib,urllib.request,json,hashlib,subprocess,tarfile,io,gzip,xml.etree.ElementTree as ET
src,out,tag,scope=sys.argv[1:]
sys.path.insert(0,str(pathlib.Path(src)/'tools/releases'))
import pacman_repo,pkgrepo
out=pathlib.Path(out);out.mkdir(mode=0o700,parents=True,exist_ok=True)
gpg=out/'gnupg';gpg.mkdir(mode=0o700,exist_ok=True)
base='https://pkg.put.gd/'+('lab/' if scope=='lab' else '')
def fetch(rel):
 p=out/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with urllib.request.urlopen(base+rel,timeout=600) as r:p.write_bytes(r.read())
 print('FETCH',base+rel,hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
 return p
key=pathlib.Path(src)/'packaging/linux/repo/keys/putgd-nightly.asc'
subprocess.run(['gpg','--homedir',str(gpg),'--batch','--import',str(key)],check=True)
def verify(p,s=None):
 c=['gpg','--homedir',str(gpg),'--batch','--status-fd=1','--verify']+([str(s),str(p)] if s else [str(p)])
 r=subprocess.run(c,capture_output=True,text=True);print(r.stdout,r.stderr,flush=True);assert r.returncode==0
 assert '4032E28D893BAF66F4AC23D9A11D38D55536B371' in r.stdout
sums_file=fetch('releases/'+tag+'/SHA256SUMS')
sums=pkgrepo.update_feed.parse_sums(sums_file.read_text())
original=pkgrepo.update_feed.parse_sums((out.parent/'verified-release/SHA256SUMS').read_text())
assert all(original[n]==h for n,h in sums.items())
assert pkgrepo.verify_minisign(pathlib.Path(src)/'packaging/linux/repo/keys/putgd-nightly.minisign.pub',sums_file,fetch('releases/'+tag+'/SHA256SUMS.minisig'))
asset=next(n for n in sums if n.endswith('-archlinux-x86_64.pkg.tar.zst'))
prefix='pacman/x86_64/nightly/'
db=fetch(prefix+'putgd-nightly.db');verify(db,fetch(prefix+'putgd-nightly.db.sig'))
pacman_repo.check_database(db.read_bytes(),asset,sums[asset])
pkg=fetch(prefix+asset);assert hashlib.sha256(pkg.read_bytes()).hexdigest()==sums[asset]
verify(pkg,fetch(prefix+asset+'.sig'))
for label in ('ubuntu24.04','ubuntu26.04','debian13'):
 rel='apt/'+label+'/dists/nightly/'
 release=fetch(rel+'Release');ir=fetch(rel+'InRelease');verify(ir);verify(release,fetch(rel+'Release.gpg'))
 assert pkgrepo.clearsigned_body(ir)==release.read_text()
 packages=fetch(rel+'main/binary-amd64/Packages')
 digest=hashlib.sha256(packages.read_bytes()).hexdigest();assert digest in release.read_text()
 text=packages.read_text();name=next(n for n in sums if n.endswith('-'+label+'-x86_64.deb'))
 assert sums[name] in text and tag[1:].replace('-nightly','~nightly') in text
repomd=fetch('rpm/fedora/44/x86_64/nightly/repodata/repomd.xml')
ns={'r':'http://linux.duke.edu/metadata/repo'}
for data in ET.fromstring(repomd.read_bytes()).findall('r:data',ns):
 location=data.find('r:location',ns).attrib['href'];p=fetch('rpm/fedora/44/x86_64/nightly/'+location)
 ck=data.find('r:checksum',ns);assert hashlib.new(ck.attrib['type'],p.read_bytes()).hexdigest()==ck.text
 if data.attrib['type']=='primary':
  content=(gzip.decompress(p.read_bytes()) if p.name.endswith('.gz') else subprocess.check_output(['zstd','-dc',str(p)]) if p.name.endswith('.zst') else p.read_bytes())
  assert tag[1:].replace('-nightly','~nightly').encode() in content
receipt=json.loads(fetch('receipts/'+tag+'.json').read_text())
assert receipt['result']=='published'
for rpm in receipt['rpm']:
 assert original[rpm['asset']]==rpm['githubSha256']
 p=fetch('rpm/fedora/44/x86_64/nightly/Packages/'+rpm['file'])
 assert hashlib.sha256(p.read_bytes()).hexdigest()==rpm['repoSha256']
 assert pkgrepo.verify_rpm(key,p)
print('PASS CDN pacman signatures and release hash; all apt signatures/index hashes; dnf metadata hashes and version',flush=True)
