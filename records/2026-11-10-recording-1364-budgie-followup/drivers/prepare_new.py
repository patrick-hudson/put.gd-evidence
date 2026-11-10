from pathlib import Path
import hashlib
src=Path('/home/patrick/work/putgd-evidence/2026-11-09-features/acceptance-1364/record_run-hide-bar.py')
s=src.read_text();Path('/tmp/b1364-followup/record_run-hide-bar-original.py').write_text(s)
s=s.replace('import argparse\n','import argparse\nimport shutil\n')
old="        result['clips'] = {}";assert s.count(old)==1
s=s.replace(old,"        preserved = self.run / 'preserved'\n        preserved.mkdir(mode=0o700, exist_ok=True)\n        for source in (working, copy):\n            if source.is_file(): shutil.copy2(source, preserved / source.name)\n"+old)
old="        checked = subprocess.run([sys.executable, str(HERE / 'cover_player.py'), 'check-frame', str(frame),"
assert s.count(old)==1
s=s.replace(old,"        (self.run / 'preserved').mkdir(mode=0o700, exist_ok=True)\n        shutil.copy2(frame, self.run / 'preserved' / frame.name)\n"+old)
old="        checked = subprocess.run([sys.executable, str(HERE / 'cover_player.py'), *check], capture_output=True, text=True)";assert s.count(old)==1
s=s.replace(old,"        (self.run / 'preserved').mkdir(mode=0o700, exist_ok=True)\n        shutil.copy2(saved, self.run / 'preserved' / saved.name)\n"+old)
s=s.replace("            result['canvas'] = ready.get('canvas')","            result['canvas'] = ready.get('canvas')\n            result['residentLauncherPid'] = self.resident.pid")
s=s.replace("        info = {}\n        while time.monotonic() - began < seconds + 45:","        entry['operationId'] = operation\n        info = {}\n        while time.monotonic() - began < seconds + 45:")
Path('/tmp/b1364-followup/record_run_new.py').write_text(s)
print('original',hashlib.sha256(src.read_bytes()).hexdigest(),'preserving',hashlib.sha256(s.encode()).hexdigest())
