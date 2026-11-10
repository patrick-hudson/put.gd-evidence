from pathlib import Path
p=Path('/tmp/b1364/record_run.py');s=p.read_text();assert __import__('hashlib').sha256(s.encode()).hexdigest()=='e5f1764ff963e974c3755267abb932ecc9aaccf0b23446b89767026fbe68398e'
# Keep the original guards. Preserve owned guest artifacts before any destructive guard.
s=s.replace('import argparse\n','import argparse\nimport shutil\n')
s=s.replace("        result['canvas'] = ready.get('canvas')", "        result['canvas'] = ready.get('canvas')") # preserve indentation below via exact match
old="            result['canvas'] = ready.get('canvas')"
assert s.count(old)==1;s=s.replace(old,old+"\n            result['residentLauncherPid'] = self.resident.pid\n            result['hiddenAtReady'] = self.cli(build, 'recording.overlay', {'id': rid, 'visible': False})")
old="        result['clips'] = {}";assert s.count(old)==1
s=s.replace(old,"        preserved = self.run / 'preserved'\n        preserved.mkdir(mode=0o700, exist_ok=True)\n        for source in (working, copy):\n            if source.is_file(): shutil.copy2(source, preserved / source.name)\n"+old)
old="        checked = subprocess.run([sys.executable, str(HERE / 'cover_player.py'), 'check-frame', str(frame),"
assert s.count(old)==1
s=s.replace(old,"        (self.run / 'preserved').mkdir(mode=0o700, exist_ok=True)\n        shutil.copy2(frame, self.run / 'preserved' / frame.name)\n"+old)
old="        checked = subprocess.run([sys.executable, str(HERE / 'cover_player.py'), *check], capture_output=True, text=True)"
assert s.count(old)==1
s=s.replace(old,"        (self.run / 'preserved').mkdir(mode=0o700, exist_ok=True)\n        shutil.copy2(saved, self.run / 'preserved' / saved.name)\n"+old)
s=s.replace("        info = {}\n        while time.monotonic() - began < seconds + 45:","        entry['operationId'] = operation\n        info = {}\n        while time.monotonic() - began < seconds + 45:")
Path('/tmp/b1364-followup/record_run.py').write_text(s)
