# Run under the physical desktop lock. Unpack only the CI AppImage and staged browser.
import os,sys,subprocess,json,zipfile,shutil,hashlib
from pathlib import Path
P=Path.home()/'work/sfa15';host=sys.argv[1]
assert hashlib.sha256((P/'candidate.AppImage').read_bytes()).hexdigest()=='b6d8079774125b5fec692b7b8614bfabf0ea027ecc9118abda694fbfdab19bec'
assert len(str((P/'r/putgd/session.sock').resolve()).encode())<=107
print('resolved socket',str((P/'r/putgd/session.sock').resolve()),'bytes',len(str((P/'r/putgd/session.sock').resolve()).encode()),flush=True)
for n in ['r','tools']:(P/n).mkdir(mode=0o700,exist_ok=True)
os.chmod(P/'candidate.AppImage',0o700);os.chmod(P/'cli',0o700)
assert not (P/'squashfs-root').exists()
with (P/'extract.log').open('w') as f:subprocess.run([str(P/'candidate.AppImage'),'--appimage-extract'],cwd=P,stdout=f,check=True)
if (P/'chrome.zip').exists():
 with zipfile.ZipFile(P/'chrome.zip') as z:z.extractall(P/'tools')
 for n in ['chrome','chrome_crashpad_handler','chrome_sandbox']:
  if (P/'tools/chrome-linux64'/n).exists():os.chmod(P/'tools/chrome-linux64'/n,0o755)
if host=='m74':
 shutil.copyfile(P/'accept-m74.py',P/'accept.py')
 s=(P/'accept.py').read_text().replace("for n in ['firefox','chrome-linux64']:","for n in ['firefox']:")
 (P/'accept.py').write_text(s)
else:
 base=P/'tools/firefox';base.mkdir(exist_ok=True)
 (base/'firefox').write_text('#!/bin/sh\nexec /usr/bin/firefox "$@"\n');os.chmod(base/'firefox',0o700)
 s=(P/'accept.py').read_text();start=s.index('for n in [');end=s.index('found=dict',start);s=s[:start]+s[end:];(P/'accept.py').write_text(s)
with (P/'mcp-extract.log').open('w') as f:subprocess.run(['tar','-xf',str(P/'mcp.tar')],cwd=P,stdout=f,check=True)
s=(P/'extra.py').read_text().replace("['toolbox','run','-c','putgd-build',str(P/'tools/mcp/.venv/bin/python'),str(P/'mcptest.py')]", "[os.environ['SFA_MCP_PYTHON'],str(P/'mcptest.py')]")
s=s.replace('import accept as A,json','import os\nimport accept as A,json');(P/'extra.py').write_text(s)
print('prepared',host,flush=True)
