import sys,time,json
from pathlib import Path
sys.path.insert(0,str(Path.home()/'work/i1363/tools/lab'))
import lab
R='ac5';RUN=Path.home()/'work/i1363/work/lab-runs'/R;E=Path.home()/'work/i1363/work/acceptance-1363'/R
print(lab.guest_session(RUN,"setsid -f xmessage -geometry 600x300+100+200 -title 'Synthetic MCP capture target' -buttons Done:0 'put.gd capture acceptance: synthetic window content, build4498' >/tmp/p1363-mcp-synthetic-window.log 2>&1 </dev/null"))
time.sleep(1)
print('Synthetic X11 target opened; verify/focus it before writing ready witness')
