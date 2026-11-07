#!/usr/bin/env python3
# drive.py W H move X Y | drag X1 Y1 X2 Y2 | click X Y   (screen pixels)
import json, socket, sys, time
W, H = int(sys.argv[1]), int(sys.argv[2]); cmd = sys.argv[3]; a = [int(v) for v in sys.argv[4:]]
s = socket.socket(socket.AF_UNIX); s.connect('/run/user/1000/putgd-lab-input.sock'); f = s.makefile('rw'); f.readline()
def send(ev):
    f.write(json.dumps({'execute': 'input-send-event', 'arguments': {'events': ev}}) + '\n'); f.flush(); f.readline()
f.write(json.dumps({'execute': 'qmp_capabilities'}) + '\n'); f.flush(); f.readline()
def pos(x, y): return [{'type': 'abs', 'data': {'axis': 'x', 'value': round(x * 32767 / (W - 1))}}, {'type': 'abs', 'data': {'axis': 'y', 'value': round(y * 32767 / (H - 1))}}]
def btn(d): return [{'type': 'btn', 'data': {'down': d, 'button': 'left'}}]
if cmd == 'move': send(pos(*a))
elif cmd == 'click': send(pos(*a)); time.sleep(.15); send(btn(True)); time.sleep(.1); send(btn(False))
elif cmd == 'drag':
    x1, y1, x2, y2 = a; send(pos(x1, y1)); time.sleep(.3); send(btn(True)); time.sleep(.3)
    for i in range(1, 31): send(pos(x1 + (x2 - x1) * i / 30, y1 + (y2 - y1) * i / 30)); time.sleep(.03)
    time.sleep(.3); send(btn(False))
f.close(); s.shutdown(socket.SHUT_WR); s.recv(1); s.close()
