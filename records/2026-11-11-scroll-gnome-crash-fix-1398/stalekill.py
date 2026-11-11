#!/usr/bin/env python3
"""stalekill.py RUN OUT.png: prepare, kill the helper at once, wait 4 s with the resident alive, screenshot the wall."""
import sys, time, json, os, signal
import fx5, rfb
run = fx5.Run(sys.argv[1])
shell = fx5.shell_pid()
run.start_resident()
v = run.rpc('scroll.prepare', {'rect': fx5.RECT})
pids = run.helper_pids()
for pid in pids:
    os.kill(pid, signal.SIGKILL)
time.sleep(4)
vnc = rfb.RFB(5901); vnc.screenshot(sys.argv[2]); vnc.sock.close()
print(json.dumps({'prepare': v['state'], 'killed': pids, 'after': run.rpc('scroll.inspect', {'id': v['id']}, check=False).get('state'), 'shell': shell, 'shellAfter': fx5.shell_pid()}))
run.stop_resident()
