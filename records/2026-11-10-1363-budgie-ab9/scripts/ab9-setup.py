import subprocess,json,pathlib,shlex
root=pathlib.Path('/home/patrick/work/i1363');s=json.loads((root/'work/lab-runs/ab9/state.json').read_text());k=s['bootstrap_key'];opts=['-i',k,'-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+s['known_hosts']]
subprocess.run(['scp','-q','-P','22449']+opts+[str(root/'tools/lab/wayland_pointer.py'),str(root/'tools/lab/wayland_toplevels.py'),'lab@127.0.0.1:/tmp/'],check=True)
cmd='printf "%s\\n" "export XDG_RUNTIME_DIR=/run/user/$(id -u)" "export WAYLAND_DISPLAY=$(basename $(find /run/user/$(id -u) -maxdepth 1 -type s -name wayland-\\* | head -1))" "export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus" > /tmp/env.sh; rpm -q budgie-desktop labwc; cat /etc/os-release'
p=subprocess.run(['ssh','-n','-p','22449']+opts+['lab@127.0.0.1',cmd],capture_output=True,text=True);(root/'work/acceptance-1363/ab9/guest-versions.log').write_text(p.stdout+p.stderr)
