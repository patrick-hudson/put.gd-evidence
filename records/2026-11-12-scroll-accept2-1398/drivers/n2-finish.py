from pathlib import Path
import sys,json,subprocess,time,shlex,ast
from PIL import Image
B=Path('/home/patrick/work/sa2lab');D=Path('/home/patrick/work/sa2vm');sys.path.insert(0,str(B/'tools/lab'));sys.path.insert(0,str(D/'fixtures'));import lab,scroll_run,argparse
r=B/'work/lab-runs/sa2n2';o=D/'ev/sa2n2/selectorless'
def cmd(s):return lab.guest_session(r,s+' 2>&1 || true',timeout=240)
prep="""from pathlib import Path
import subprocess,json,time
p=Path('/tmp/s23');e=json.loads((p/'env.json').read_text())
def rpc(m,a={}):return json.loads(subprocess.run(['/usr/bin/putgd-cli','--socket',str(p/'r/putgd/session.sock'),m,json.dumps(a)],env=e,text=True,capture_output=True).stdout)
v=rpc('scroll.prepare',{'rect':[100,200,960,600],'maxHeight':40000})['result'];ident=v['id']
while v['state']!='ready':time.sleep(.1);v=rpc('scroll.inspect',{'id':ident})['result']
(p/'prepared.json').write_text(json.dumps(v));time.sleep(1);print(json.dumps(v))
"""
(o/'prepare.log').write_text(cmd('python3 -c '+shlex.quote(prep)));im=Image.open(lab.screenshot(r,'native-ready-after-prepare')['path']).convert('RGB').crop((100,200,1060,800));im.save(o/'ready-after-prepare.png');v=scroll_run.verify(o/'ready-after-prepare.png',argparse.Namespace(scale=1,height=600,rows=60,first_pixel=0,header=0,footer=0,code_width=960,format='fixture',scrollbar=0));(o/'ready-after-prepare-verification.json').write_text(json.dumps(v,indent=2));print('READY verifier',v['pass'],v.get('unexpectedPixels'),flush=True)
tree=ast.parse((D/'selectorless-n2.py').read_text());code=next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='code' for t in n.targets));code=code.replace("v=rpc('scroll.prepare',{'rect':[100,200,960,600],'maxHeight':40000})", "v=json.loads((P/'prepared.json').read_text())").replace("off=(P/'helper.log').stat().st_size if (P/'helper.log').exists() else 0","off=0")
(o/'explicit.log').write_text(cmd('python3 -c '+shlex.quote(code)));print((o/'explicit.log').read_text()[-1200:],flush=True)
(o/'explicit-ruler').mkdir(exist_ok=True)
for n in ['capture.png','result.json','helper.log','verification.json']:lab.get(r,'/tmp/s23/cases/explicit-ruler/'+n,o/'explicit-ruler'/n)
for n in ['version.json','capabilities.json','refusal.json','rpc.jsonl','socket-preflight.json','dashboard-preparation.json']:lab.get(r,'/tmp/s23/'+n,o/n)
(o/'done').write_text('done');subprocess.run(['python3',str(D/'export-host.py'),'n2'],check=True)
