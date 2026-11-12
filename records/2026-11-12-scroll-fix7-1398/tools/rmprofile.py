# Deletes a browser profile this harness made, file by file from its own listing.
import sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
assert root.parent == Path.home() / "work/sf7" and root.name.startswith("profile-"), root
files = [p for p in root.rglob("*") if not p.is_dir() or p.is_symlink()]
dirs = sorted([p for p in root.rglob("*") if p.is_dir() and not p.is_symlink()], key=lambda p: -len(p.parts))
for f in files: f.unlink()
for d in dirs: d.rmdir()
root.rmdir()
print("deleted", len(files), "files", len(dirs) + 1, "directories")
