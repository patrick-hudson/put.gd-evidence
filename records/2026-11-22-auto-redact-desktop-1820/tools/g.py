"""d69-side helper for a lab guest: g.py RUN (stage DIR... | start ARGS | dc JSON | get REMOTE LOCAL | sh CMD | root)."""
import json, os, shlex, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'tools/lab'))
import lab
run = Path(sys.argv[1]); op = sys.argv[2]; rest = sys.argv[3:]
rootfile = run / 'acc-root'
if op == 'stage':
    target = lab.ssh(run, 'mktemp -d /tmp/a21.XXXXXX\n').strip()
    rootfile.write_text(target + '\n')
    for p in rest:
        lab.put(run, p, target + '/' + Path(p).name)
    t = shlex.quote(target)
    lab.ssh(run, f'cd {t} && chmod u+x candidate.AppImage && ./candidate.AppImage --appimage-extract >extract.log 2>&1 && mkdir -p fx && tar xf fx.tar -C fx && echo ok\n', timeout=300)
    print(target)
elif op == 'root':
    print(rootfile.read_text().strip())
elif op == 'start':
    target = rootfile.read_text().strip(); info = lab.state(run)
    app = target + '/squashfs-root'
    port = 55900
    args = lab.ssh_args(run); endpoint = args.pop()
    args += ['-T', '-o', 'ExitOnForwardFailure=yes', '-R', f'127.0.0.1:{port}:127.0.0.1:{info["vnc_display"] + 5900}', endpoint]
    cli = f'env LD_LIBRARY_PATH={app}/usr/lib:{app}/usr/lib/putgd {app}/usr/bin/putgd-cli'
    cmd = ['python3', '-u', target + '/driver.py', target, '--vnc', str(port), '--app', app + '/AppRun', '--cli', cli, *rest]
    log = open(run / 'acc-driver.log', 'a')
    p = subprocess.Popen([*args, shlex.join(cmd)], stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    (run / 'acc-driver.pid').write_text(str(p.pid)); print(p.pid)
elif op == 'dc':
    target = rootfile.read_text().strip()
    print(lab.ssh(run, f'python3 {target}/dc.py {target}/c.sock {shlex.quote(rest[0])}\n', timeout=900), end='')
elif op == 'get':
    lab.get(run, rest[0], rest[1])
elif op == 'sh':
    print(lab.ssh(run, rest[0] + '\n', timeout=300), end='')
