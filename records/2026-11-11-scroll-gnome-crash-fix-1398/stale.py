#!/usr/bin/env python3
"""stale.py RUN DELAY OUT.png: prepare, cancel after DELAY, wait 4 s with the resident alive, screenshot the wall."""
import sys, time, json
import fx5, rfb
run = fx5.Run(sys.argv[1]); delay = float(sys.argv[2])
shell = fx5.shell_pid()
run.start_resident()
v = run.rpc('scroll.prepare', {'rect': fx5.RECT})
time.sleep(delay)
c = run.rpc('scroll.cancel', {'id': v['id']})
time.sleep(4)
vnc = rfb.RFB(5901); vnc.screenshot(sys.argv[3]); vnc.sock.close()
print(json.dumps({'prepare': v['state'], 'cancel': c['state'], 'shell': shell, 'shellAfter': fx5.shell_pid(), 'helpers': run.helper_pids()}))
run.stop_resident()
