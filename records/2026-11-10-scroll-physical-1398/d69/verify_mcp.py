import sys,json,hashlib,shutil,subprocess
from pathlib import Path
p=Path('/tmp/sp1398');sha=sys.argv[1]
for f in (p/'archive').rglob('*.png'):
 if hashlib.sha256(f.read_bytes()).hexdigest()==sha:
  shutil.copyfile(f,p/'mcp-capture.png');break
else:raise RuntimeError('no PNG for MCP SHA')
package=next(x for x in p.iterdir() if x.suffix in ('.rpm','.deb') and '4635' in x.name)
subprocess.run(['python3',str(p/'scroll_run.py'),'--out',str(p/'mcp-verified'),'--package',str(package),'--verify-png',str(p/'mcp-capture.png'),'--format','fixture','--rows','60'])
