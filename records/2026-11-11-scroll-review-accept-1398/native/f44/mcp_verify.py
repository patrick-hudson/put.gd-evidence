import pass2,json,sys,hashlib,shutil,argparse
from pathlib import Path
import scroll_run
P=pass2.P;sha=sys.argv[1];out=P/'mcp';out.mkdir()
for f in (P/'archive').rglob('*.png'):
 if hashlib.sha256(f.read_bytes()).hexdigest()==sha:shutil.copyfile(f,out/'capture.png');break
else:raise RuntimeError('MCP PNG absent')
a=argparse.Namespace(scale=1,height=24000,rows=600,first_pixel=0,header=0,footer=0,code_width=960,format='fixture',scrollbar=0)
r={'verification':scroll_run.verify(out/'capture.png',a),'sha256':sha,'identity':json.loads((P/'identity.json').read_text())};(out/'result.json').write_text(json.dumps(r,indent=2));print(json.dumps(r['verification']))
