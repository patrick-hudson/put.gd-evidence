# Deletes directories this harness made under ~/work/sf7, file by file from their own listing.
#   rmowned.py NAME [NAME ...]     NAME is one of c d s cache r archive stage, or profile-*
import sys
from pathlib import Path
base = Path.home() / "work/sf7"
for name in sys.argv[1:]:
    assert name in ("c", "d", "s", "cache", "r", "archive") or name.startswith("profile-"), name
    root = (base / name)
    if not root.exists():
        continue
    assert root.resolve().parent == base.resolve(), root
    files = [p for p in root.rglob("*") if p.is_symlink() or not p.is_dir()]
    dirs = sorted([p for p in root.rglob("*") if p.is_dir() and not p.is_symlink()], key=lambda p: -len(p.parts))
    for f in files: f.unlink()
    for d in dirs: d.rmdir()
    root.rmdir()
    print("deleted", name, len(files), "files", len(dirs) + 1, "directories")
