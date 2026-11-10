#!/usr/bin/env python3
"""#1361: the test-results panel (picture 15), drawn from the real outputs of this build.

  python3 panel1361.py --ctest FILE --check FILE --title TEXT --out FILE

--ctest is the output of `ctest -R http_uploader -V`; --check the report of check_uploads.py.
"""
import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser()
parser.add_argument('--ctest', required=True)
parser.add_argument('--check', required=True)
parser.add_argument('--title', required=True)
parser.add_argument('--out', required=True)
options = parser.parse_args()

mono = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
bold = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
regular, strong = ImageFont.truetype(mono, 15), ImageFont.truetype(bold, 15)
WHITE, GREEN, BLUE, GREY = (236, 236, 236), (126, 211, 135), (140, 190, 255), (190, 190, 190)

lines = [(options.title, WHITE, strong), ('', WHITE, regular), ('$ ctest -R http_uploader -V', BLUE, strong)]
for line in Path(options.ctest).read_text().splitlines():
    line = re.sub(r'^\d+: ', '', line)
    if line.startswith('********* Start testing of'):
        lines.append((line, GREY, regular))
    elif line.startswith('Totals:') or re.match(r'^\s*\d+/\d+ Test\s+#\d+:', line) or '% tests passed' in line:
        lines.append((re.sub(r'\s{2,}', '   ', line.strip()) if 'Test' in line and '#' in line else line.strip(), GREEN, regular))
report = json.loads(Path(options.check).read_text())
lines += [('', WHITE, regular), ('$ check_uploads.py --allow-insecure-http   (headless private resident, three real receivers)', BLUE, strong)]
for entry in report['receivers']:
    deletion = entry.get('deletion') or {}
    removed = ('removed, link then HTTP %s' % deletion.get('linkStatusAfter')) if deletion.get('remoteStatus') == 'removed' else 'not offered (no deletion URL)' if deletion.get('offered') is False else str(deletion)
    lines.append(('%-9s  passed=%s  test=%s  upload=%s  link=HTTP %s  deletion=%s' % (entry['receiver'], entry.get('passed'), (entry.get('test') or {}).get('state'),
                                                                                    (entry.get('upload') or {}).get('uploadStatus'), (entry.get('upload') or {}).get('linkStatus'), removed), GREEN, regular))
lines.append(('filesHoldingAToken=%s  diagnosticsPackageScanned=%s  cleanupError=%s  passed=%s' % (report['filesHoldingAToken'], report['diagnosticsPackageScanned'], report['cleanupError'], report['passed']), GREEN, regular))

image = Image.new('RGB', (1240, 60 + 24 * len(lines) + 110), (27, 27, 30))
draw = ImageDraw.Draw(image)
rows = {}
for index, (text, colour, font) in enumerate(lines):
    y = 60 + 24 * index
    draw.text((24, y), text, fill=colour, font=font)
    rows[text[:24]] = y
image.save(options.out)
print(json.dumps({'size': image.size, 'rows': [[y, text[:60]] for (text, _, _), y in zip(lines, range(60, 60 + 24 * len(lines), 24))]}, indent=0))
