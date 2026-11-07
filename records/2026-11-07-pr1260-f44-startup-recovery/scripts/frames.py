#!/usr/bin/env python3
"""Save the desktop's VNC frame about once a second: frames.py PORT OUT SECONDS."""
import pathlib, sys, time
sys.path.insert(0, str(pathlib.Path.home() / 'work/wA1252/tools/lab'))
from rfb import RFB

port, out, seconds = int(sys.argv[1]), pathlib.Path(sys.argv[2]), float(sys.argv[3])
client = RFB(port)
start = time.time()
index = 0
while time.time() - start < seconds:
    taken = time.time()
    path = out / f'{index:02d}-{taken:.3f}.png'
    client.screenshot(str(path))
    print(f'{index} {taken:.3f} {path.name}', flush=True)
    index += 1
    time.sleep(max(0.0, 1.0 - (time.time() - taken)))
client.close()
