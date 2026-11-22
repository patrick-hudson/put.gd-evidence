"""Compare originally captured pixels in each build pair, independently of marks."""
import hashlib
import sys
from pathlib import Path
from PIL import Image, ImageChops
from capture import write_json

base = Path(sys.argv[1]) / 'results'
scenes = {}
for candidate in sorted((base / 'candidate').glob('*-verify.json')):
    scene = candidate.name.removesuffix('-verify.json')
    paths = [base / version / f'{scene}-orig.png' for version in ('nightly', 'candidate')]
    if not all(path.exists() for path in paths):
        continue
    hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
    identical = hashes[0] == hashes[1]
    if not identical:
        before, after = (Image.open(path).convert('RGBA') for path in paths)
        identical = before.size == after.size and not any(
            band.getbbox() for band in ImageChops.difference(before, after).split())
    scenes[scene] = {'originalPngSha256Nightly': hashes[0], 'originalPngSha256Candidate': hashes[1],
                     'originalPixelsIdentical': identical}
    print(scene, 'same source pixels' if identical else 'different source pixels')
write_json(base.parent / 'comparison.json', scenes)
