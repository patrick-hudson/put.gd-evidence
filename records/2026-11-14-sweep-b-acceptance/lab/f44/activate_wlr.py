#!/usr/bin/env python3
import sys,struct,time
import wayland_toplevels as w
c=w.Client(w.socket_path());c.snapshot();c.bind('wl_seat',1,'seat');seat=c.next_id-1;c.sync()
matched=[h for h,v in c.wlr.items() if v.get('current',{}).get('title')=='put.gd independent GTK clipboard fixture' and not v.get('closed')]
assert len(matched)==1
c.send(w.message(matched[0],4,struct.pack('<I',seat)));c.sync();time.sleep(.2);c.sock.close()
