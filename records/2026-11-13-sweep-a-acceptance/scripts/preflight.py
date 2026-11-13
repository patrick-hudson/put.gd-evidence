#!/usr/bin/env python3
"""Read-only builder inventory. No GUI input, package mutation or VM launch."""
import subprocess,json,pathlib,concurrent.futures
ROOT=pathlib.Path('/tmp/sa1113')
HOSTS={'f44':'70','d69':'69','k72':'72','m74':'74','aurora-amd':'71'}
def one(item):
 host,ip=item
 args=['ssh','-n','-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','-o',f'UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/{host}/known_hosts',f'patrick@192.168.68.{ip}']
 p=subprocess.run(args+["date -u; uptime; nproc; df -h /home/patrick; df -i /home/patrick; command -v qemu-system-x86_64; test -r /dev/kvm && echo kvm-readable; dpkg-query -W putgd 2>/dev/null || rpm -q putgd; pgrep -c qemu-system || true"],capture_output=True,text=True,timeout=25)
 (ROOT/f'{host}-preflight.txt').write_text(p.stdout+p.stderr)
 return host,p.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 for value in pool.map(one,HOSTS.items()): print(value)
