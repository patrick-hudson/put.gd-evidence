# Quit the pass2 resident of ~/work/sopus/s and end its own processes by PID (found by their XDG_CONFIG_HOME).
from pathlib import Path
import os, time
import pass2 as p
P = p.P
try: p.rpc('ui.quit')
except Exception as e: print('ui.quit', e)
try: p.rpc('app.quit')
except Exception as e: print('app.quit', e)
time.sleep(3); owned = []
for q in Path('/proc').iterdir():
    if not q.name.isdigit(): continue
    try:
        if ('XDG_CONFIG_HOME=' + str(P / 'c')).encode() in (q / 'environ').read_bytes().split(b'\0'): owned.append((int(q.name), (q / 'comm').read_text().strip()))
    except OSError: pass
for pid, comm in owned:
    try: os.kill(pid, 15)
    except ProcessLookupError: pass
print('owned', owned)
