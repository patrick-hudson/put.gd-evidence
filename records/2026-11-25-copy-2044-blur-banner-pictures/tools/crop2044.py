#!/usr/bin/env python3
"""Crop the #2044 frames to the review window's blur messages and write the annotation spec.
usage: crop2044.py FRAMES_DIR OUT_DIR SPEC"""
import json
import sys
from pathlib import Path
from PIL import Image
frames, out, spec_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
CROPS = {  # name: (scene, crop box in the frame, highlight rect in the crop for before, after)
    '1-review-blur-banner': ('blur-selected-folded', (160, 60, 1600, 145), {'before': [430, 38, 382, 40], 'after': [430, 38, 420, 40]}),
    '2-review-panel-blur-sentence': ('blur-selected-wide', (1160, 150, 1440, 340), {'before': [8, 136, 266, 44], 'after': [8, 136, 266, 44]}),
    '3-review-blur-prompt': ('blur-armed', (160, 92, 1060, 144), {'before': [444, 10, 310, 32], 'after': [444, 10, 330, 32]}),
}
spec = {}
for label in ('before', 'after'):
    for name, (scene, box, marks) in CROPS.items():
        file = '%s-%s.png' % (name, label)
        Image.open(frames / ('%s-%s-full.png' % (label, scene))).convert('RGB').crop(box).save(out / file)
        spec[file] = [{'kind': 'rectangle', 'rect': marks[label], 'color': '#D7263D', 'width': 3}]
spec_path.write_text(json.dumps(spec, indent=1))
print('\n'.join(sorted(spec)))
