from pathlib import Path
import hashlib, datetime
root=Path.home()/'work/ubuntu-mirror-1381'
archive=root.parent/'ubuntu-mirror-1381-source.tar'
expected='5efb05bee4a374bc59b4572684344b3a258732f2302b19e4a1a2bc9c2424cf93'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
files=['evidence/linux26.log','evidence/package26.log','evidence/linux24.log','evidence/sanitizers.log','evidence/ci-log-capture.png','focused-tests-payload.log','.github/workflows/ci.yml','.github/workflows/ci.nightly.yml','.github/workflows/ci.metadata.yml','.github/workflows/package.yml','render-evidence.py','tests/desktop/pipewire/ci_check.sh','tests/ci/__pycache__/test_ubuntu_mirrors.cpython-313.pyc','tests/ci/test_ubuntu_mirrors.py','metadata-regression.log','focused-tests.log','baseline-final.log','baseline-tests.log']
for name in files:
 p=root/name
 assert p.is_file() and not p.is_symlink(), p
for name in files:(root/name).unlink()
for name in ['evidence','.github/workflows','.github','tests/desktop/pipewire','tests/desktop','tests/ci/__pycache__','tests/ci','tests']:(root/name).rmdir()
root.rmdir()
archive.unlink()
print(datetime.datetime.now(datetime.timezone.utc).isoformat())
print('d69: removed only 18 named lane files and their empty directories after export checksum verification.')
print('Export SHA-256:', expected)
print('Local d69-test-source.tar retains source, focused results, baseline failures and rendered evidence; restore index is d69-test-source.index.')
print('No desktop/VM/tunnel/lock was created. All test and rendering commands completed before cleanup.')
