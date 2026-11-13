from pathlib import Path
import subprocess,json,time,hashlib,shlex,datetime
r=Path.home()/'work/ocr-corpus-1428';w=r/'candidate-clean-installs';w.mkdir(mode=0o700);rows=[]
cases=[('ubuntu24','docker.io/library/ubuntu:24.04',next((r/'ubuntu24-package').glob('*.deb'))),('ubuntu26','docker.io/library/ubuntu:26.04',next((r/'ubuntu26-package').glob('*.deb'))),('debian13','docker.io/library/debian:13',r/'putgd_26.1113.4836~dev+gfe838a950216_amd64.deb'),('fedora44','registry.fedoraproject.org/fedora:44',next((r/'fedora44-package').glob('*.rpm'))),('arch','docker.io/library/archlinux:latest',next((r/'arch-package').glob('*.pkg.tar.zst')))]
for distro,image,pkg in cases:
 if datetime.datetime.now(datetime.timezone.utc).hour>=12:break
 name='item8-clean-1428-'+distro;log=(w/(distro+'-install.log')).open('x');pre=subprocess.run(['sudo','-n','podman','image','exists',image]).returncode==0;p=subprocess.run(['sudo','-n','podman','run','--name',name,'--network=host','--security-opt','label=disable','-v',str(r)+':/case:ro','-d',image,'sleep','infinity'],capture_output=True,text=True);row={'target':distro,'image':image,'imageWasPresent':pre,'containerId':p.stdout.strip(),'createExit':p.returncode,'packageSha256':hashlib.sha256(pkg.read_bytes()).hexdigest(),'package':str(pkg.relative_to(r)),'status':'not_run'}
 if p.returncode:
  row['reason']='container create failed';rows.append(row);(w/'receipt.json').write_text(json.dumps(rows,indent=2));continue
 try:
  arg='/case/'+str(pkg.relative_to(r));q=shlex.quote(arg)
  if distro in ['ubuntu24','ubuntu26','debian13']:setup='apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends '+q;data='/usr/share/tesseract-ocr/5/tessdata';metadata=['dpkg-query','-W','-f=${Version}|${Depends}|${Recommends}','putgd']
  elif distro=='fedora44':setup='dnf install -y --setopt=install_weak_deps=False '+q;data='/usr/share/tesseract/tessdata';metadata=['rpm','-q','--requires','putgd']
  else:setup='pacman -Syu --noconfirm && pacman -U --noconfirm '+q;data='/usr/share/tessdata';metadata=['pacman','-Qi','putgd']
  row['installCommand']=setup;p=subprocess.run(['sudo','-n','podman','exec',name,'sh','-ec',setup],stdout=log,stderr=subprocess.STDOUT,timeout=600);row['installExit']=p.returncode
  if p.returncode:row['reason']='install failed';continue
  p=subprocess.run(['sudo','-n','podman','exec',name]+metadata,capture_output=True,text=True);(w/(distro+'-package-metadata.txt')).write_text(p.stdout);row['packageMetadataExit']=p.returncode
  p=subprocess.run(['sudo','-n','podman','exec',name,'sha256sum',data+'/eng.traineddata'],capture_output=True,text=True);row['englishDataSha256']=p.stdout.split()[0] if p.returncode==0 else None;row['englishDataQueryExit']=p.returncode
  cmd=['sudo','-n','podman','exec',name,'/case/test_ocr_run','--helper','/usr/bin/putgd-ocr','--data',data,'--lang','eng','--required','/case/candidate-corpus/m74-captures/m74-prose-terminal-light-100.png'];p=subprocess.run(cmd,capture_output=True,text=True,timeout=40);row.update(driverExit=p.returncode,driverStderrBytes=len(p.stderr));v=json.loads(p.stdout.strip().splitlines()[-1]);row['helperResult']=v;row['status']='measured' if p.returncode==0 and not v['error'] and v['chars']>1000 and row['englishDataSha256'] else 'not_run';print('CLEAN',distro,row['status'],v['chars'],flush=True)
 except Exception as e:row['reason']=type(e).__name__
 finally:
  subprocess.run(['sudo','-n','podman','stop',name],stdout=log,stderr=subprocess.STDOUT,timeout=20);p=subprocess.run(['sudo','-n','podman','rm',name],stdout=log,stderr=subprocess.STDOUT);row['retired']=p.returncode==0;rows.append(row);(w/'receipt.json').write_text(json.dumps(rows,indent=2))
  if not pre:
   used=subprocess.run(['sudo','-n','podman','ps','-a','--filter','ancestor='+image,'--format','{{.ID}}'],capture_output=True,text=True)
   if used.returncode==0 and not used.stdout.strip():subprocess.run(['sudo','-n','podman','rmi',image],stdout=log,stderr=subprocess.STDOUT)
print('CLEAN CAMPAIGN CLOSED',flush=True)
