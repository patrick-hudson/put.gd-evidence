import pathlib,subprocess,json
out=pathlib.Path.home()/'repo1428p4'
def run(args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=20);return {'argv':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
files=subprocess.check_output(['pacman','-Qlq','putgd'],text=True).splitlines(); rows=[]
for name in files:
 p=pathlib.Path(name)
 if not p.is_file():continue
 with p.open('rb') as f:magic=f.read(4)
 if magic!=b'\x7fELF':continue
 l=run(['ldd',name]);r=run(['readelf','-d',name])
 row={'path':name,'resolved':str(p.resolve()),'ldd':l,'readelf':r,'notFound':[x.strip() for x in (l['stdout']+l['stderr']).splitlines() if 'not found' in x],'openssl4Needed':[x.strip() for x in r['stdout'].splitlines() if '(NEEDED)' in x and ('libcrypto.so.4' in x or 'libssl.so.4' in x)]};rows.append(row)
versions={n:run(['/usr/bin/'+n,'--version-json']) for n in ['putgd','putgd-cli','putgd-ocr','putgd-ui','putgd-region','putgd-record']}
a={'packageFiles':files,'elfFiles':rows,'versionChecks':versions};(out/'p4-elf-audit.json').write_text(json.dumps(a,indent=2));print(json.dumps({'elfCount':len(rows),'files':[{'path':x['path'],'notFound':x['notFound'],'openssl4Needed':x['openssl4Needed']} for x in rows],'versions':versions},indent=2))
