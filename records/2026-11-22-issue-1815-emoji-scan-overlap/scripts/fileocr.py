#!/usr/bin/env python3
"""#1808 acceptance: one corpus image through a packaged put.gd resident's own helper.

  fileocr.py start RUN CLI LAUNCHER...   start a private offscreen resident (config, data, runtime in RUN)
  fileocr.py stop RUN CLI
  fileocr.py recognize RUN CLI IMAGE     text.recognize source=file, wait, print one JSON line

The printed line has text, totalMs (the helper job, from text.inspect timings), truncated and
peakKiB: the largest VmHWM seen on any putgd-ocr process while the job ran (sampled every 5 ms from the resident's children;
VmHWM only grows, so the last sample before exit is the job's peak to within one sample).
"""
import json, os, subprocess, sys, threading, time
from pathlib import Path


def env_for(run):
    run = Path(run)
    e = {'HOME': os.environ['HOME'], 'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'LANG': 'C.UTF-8',
         'USER': os.environ.get('USER', ''), 'QT_QPA_PLATFORM': 'offscreen'}
    for n in ('config', 'data', 'cache', 'state', 'runtime'):
        (run / n).mkdir(parents=True, exist_ok=True)
    os.chmod(run / 'runtime', 0o700)
    e.update(XDG_CONFIG_HOME=str(run / 'config'), XDG_DATA_HOME=str(run / 'data'), XDG_CACHE_HOME=str(run / 'cache'),
             XDG_STATE_HOME=str(run / 'state'), XDG_RUNTIME_DIR=str(run / 'runtime'))
    return e


def cli(env, exe, method, params, timeout=60):
    r = subprocess.run([exe, method, json.dumps(params)], env=env, capture_output=True, text=True, timeout=timeout)
    reply = json.loads(r.stdout)
    if not reply.get('ok'):
        raise RuntimeError(f"{method}: {reply.get('error')}")
    return reply.get('result') or {}


def resident_pid(run):
    return (Path(run) / 'resident.pid').read_text().strip()


def helper_pids(rpid):
    """The resident's children named putgd-ocr (read from its threads' children lists: cheap)."""
    out = []
    try:
        for t in os.listdir(f'/proc/{rpid}/task'):
            for c in Path(f'/proc/{rpid}/task/{t}/children').read_text().split():
                try:
                    if Path(f'/proc/{c}/comm').read_text().strip() == 'putgd-ocr':
                        out.append(c)
                except OSError:
                    pass
    except OSError:
        pass
    return out


def watch(stop, peak, rpid):
    known = {}
    while not stop.is_set():
        for p in helper_pids(rpid):
            try:
                for line in Path(f'/proc/{p}/status').read_text().splitlines():
                    if line.startswith('VmHWM:'):
                        v = int(line.split()[1])
                        known[p] = max(known.get(p, 0), v)
            except OSError:
                pass
        peak[0] = max(known.values(), default=0)
        time.sleep(0.005)


def caps_pid(env, exe, proc):
    """putgd --background may fork: the resident is the process that owns the session socket."""
    sock = Path(env['XDG_RUNTIME_DIR']) / 'putgd' / 'session.sock'
    out = subprocess.run(['ss', '-xlpn'], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if str(sock) in line and 'pid=' in line:
            return int(line.split('pid=')[1].split(',')[0])
    return proc.pid


def main():
    action, run, exe = sys.argv[1], sys.argv[2], sys.argv[3]
    env = env_for(run)
    if action == 'start':
        log = open(Path(run) / 'resident.log', 'a')
        proc = subprocess.Popen(sys.argv[4:], env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        for _ in range(120):
            try:
                caps = cli(env, exe, 'capabilities', {}, timeout=30)
                (Path(run) / 'resident.pid').write_text(str(caps_pid(env, exe, proc)))
                print(json.dumps(caps.get('text'))); return
            except Exception:
                time.sleep(0.5)
        sys.exit('resident did not answer')
    if action == 'stop':
        try:
            cli(env, exe, 'ui.quit', {}, timeout=30)
        except Exception as e:
            print('quit:', e)
        return
    image = sys.argv[4]
    stop, peak = threading.Event(), [0]
    t = threading.Thread(target=watch, args=(stop, peak, resident_pid(run)), daemon=True); t.start()
    op = cli(env, exe, 'text.recognize', {'source': 'file', 'path': image})
    oid = op['operationId']
    while True:
        r = cli(env, exe, 'text.inspect', {'id': oid})
        if r.get('state') in ('completed', 'failed', 'cancelled', 'canceled'):
            break
        time.sleep(0.02)
    time.sleep(0.05); stop.set(); t.join()
    if r.get('error'):
        print(json.dumps({'error': r['error']})); return
    tm = r.get('timings') or {}
    print(json.dumps({'text': r.get('text', ''), 'totalMs': tm.get('totalMs'), 'engineStartMs': tm.get('engineStartMs'),
                      'truncated': r.get('truncated'), 'peakKiB': peak[0], 'state': r.get('state')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
