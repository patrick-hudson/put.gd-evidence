#!/usr/bin/python3 -I
"""helper_watch.py OUT [NAME]: record each run of a short-lived helper (put.gd issue 1428 first light).

Needs root: it listens on the kernel's process connector, so it sees the exec
and the exit of every process without touching the one that starts them. For
each process whose name is NAME (putgd-ocr) it polls /proc/PID/status about
every half millisecond and keeps the last VmHWM (the kernel's own high-water
mark of resident memory, which only grows), then writes one JSON line with the
exit code from the exit event. Stdlib only. Stop it with SIGTERM.
"""
import json, os, signal, socket, struct, sys, threading, time

out, name = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'putgd-ocr')
NETLINK_CONNECTOR, CN_IDX_PROC, CN_VAL_PROC, NLMSG_DONE, LISTEN = 11, 1, 1, 3, 1
EXEC, EXIT = 0x00000002, 0x80000000
watched, lock = {}, threading.Lock()

def poll(pid, entry):
    path = f'/proc/{pid}/status'
    while not entry.get('done'):
        try:
            with open(path) as status:
                for line in status:
                    if line.startswith('VmHWM:'):
                        entry['peakRssKb'] = int(line.split()[1]); entry['samples'] += 1
                    elif line.startswith('Threads:'):
                        entry['maxThreads'] = max(entry['maxThreads'], int(line.split()[1]))
        except OSError:
            break
        time.sleep(.0005)

s = socket.socket(socket.AF_NETLINK, socket.SOCK_DGRAM, NETLINK_CONNECTOR)
s.bind((os.getpid(), CN_IDX_PROC))
s.send(struct.pack('=IHHII', 16 + 20 + 4, NLMSG_DONE, 0, 0, os.getpid()) + struct.pack('=IIIIHH', CN_IDX_PROC, CN_VAL_PROC, 0, 0, 4, 0) + struct.pack('=I', LISTEN))
signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
log = open(out, 'a', buffering=1)
log.write(json.dumps({'watching': name, 'since': time.time()}) + '\n')
while True:
    data = s.recv(8192)
    if len(data) < 52 + 16:
        continue
    what, cpu, stamp = struct.unpack_from('=IIQ', data, 36)
    if what == EXEC:
        pid, tgid = struct.unpack_from('=II', data, 52)
        try:
            comm = open(f'/proc/{tgid}/comm').read().strip()
        except OSError:
            continue
        if comm == name and pid == tgid:
            try:
                parent = int(open(f'/proc/{tgid}/stat').read().rsplit(') ', 1)[1].split()[1])
                parent_name = open(f'/proc/{parent}/comm').read().strip()
            except (OSError, ValueError, IndexError):
                parent, parent_name = None, None
            start_ticks = open(f'/proc/{tgid}/stat').read().rsplit(') ', 1)[1].split()[19]
            entry = {'startTicks': start_ticks, 'pid': tgid, 'parent': parent, 'parentName': parent_name, 'execNs': stamp, 'peakRssKb': None, 'samples': 0, 'maxThreads': 0}
            watched[tgid] = entry
            log.write(json.dumps(dict(entry, event='spawn')) + '\n')
            threading.Thread(target=poll, args=(tgid, entry), daemon=True).start()
    elif what == EXIT:
        pid, tgid, code, sig = struct.unpack_from('=IIII', data, 52)
        if pid == tgid and tgid in watched:
            entry = watched.pop(tgid); entry['done'] = True
            entry['event'] = 'exit'
            entry.update(exitCode=(code >> 8) & 0xff, exitSignal=code & 0x7f, livedMs=round((stamp - entry.pop('execNs')) / 1e6, 1))
            entry.pop('done')
            log.write(json.dumps(entry) + '\n')
