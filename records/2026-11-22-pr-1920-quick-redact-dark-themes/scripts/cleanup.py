"""Check the test-owned process scope before releasing a physical desktop."""
import os
from pathlib import Path
import sys

root = Path(sys.argv[1])
remaining = []
for proc in Path('/proc').iterdir():
    if not proc.name.isdecimal():
        continue
    try:
        if proc.stat().st_uid != os.getuid():
            continue
        args = (proc / 'cmdline').read_bytes().strip(b'\0').split(b'\0')
    except (ProcessLookupError, FileNotFoundError, PermissionError):
        continue
    if int(proc.name) in (os.getpid(), os.getppid()):
        continue
    if any(arg.startswith(os.fsencode(str(root)) + b'/') for arg in args[1:]) or b'org.gnome.Terminal.QrFixture' in args:
        remaining.append((proc.name, Path(os.fsdecode(args[0])).name))
if remaining:
    raise SystemExit(f'Test-owned processes still present: {remaining}')
print('Test-owned process check passed')
