from pathlib import Path
import sys,json,subprocess,tarfile,hashlib,shutil
name,cell=sys.argv[1:];r=Path('/tmp/b1428');d=json.loads((r/(name+'-export.json')).read_text());bundle=r/('export-'+name+'.tar');subprocess.run(['python3',str(r/'remote.py'),'f44','--get',d['bundle'],str(bundle)],check=True);assert hashlib.sha256(bundle.read_bytes()).hexdigest()==d['sha256'];w=r/'guest-exports'/name;w.mkdir(parents=True)
with tarfile.open(bundle) as t:t.extractall(w,filter='data')
assert hashlib.sha256((w/'receipts.tar').read_bytes()).hexdigest()==d['guestTarSha256'];o=r/'final-evidence'/cell;o.mkdir()
with tarfile.open(w/'receipts.tar') as t:t.extractall(o,filter='data')
for failed in w.glob('*-failed-attempt.tar'):
 with tarfile.open(failed) as t:t.extractall(o/'failed-attempt',filter='data')
for f in w.iterdir():
 if f.suffix=='.json':shutil.copy2(f,o/f.name)
for f in r.glob(name+'-*'):
 if f.is_file() and f.suffix in ('.log','.json','.png','.txt'):shutil.copy2(f,o/f.name)
for f in (r/('quick-'+name)).iterdir():shutil.copy2(f,o/f.name)
p=next(o.glob('tp-*/receipt.json'));data=json.loads(p.read_text());assert data['passed'] and data['finalAcceptance']['quickRedact']['passed'];print(json.dumps({'cell':cell,'receipt':str(p),'passed':True,'adapter':data.get('adapter'),'commit':data['build']['gitCommit']}))
