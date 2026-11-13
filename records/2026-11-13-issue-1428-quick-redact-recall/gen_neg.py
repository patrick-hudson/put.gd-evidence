"""Held-out negative pages for Quick redact: ordinary interface, log, terminal
and code text with numbers, versions, dates, paths and identifiers, and no item
of any category. Throwaway, never committed."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
FONTS = ('DejaVuSans.ttf', 'DejaVuSerif.ttf', 'DejaVuSansMono.ttf', 'LiberationSans-Regular.ttf')
LINES = [
 "Release 26.1112.4660 for Ubuntu 24.04 and Fedora 44 shipped on 2026-11-12 at 14:05 UTC.",
 "Uploaded 3 files (12.4 MB) to Project Archive in 2.3 s; next sync in 15 minutes.",
 "cd /usr/share/tesseract-ocr/5/tessdata && ls -la eng.traineddata osd.traineddata",
 "git log --oneline -3 origin/feat/text-recognition",
 "Error 404: the requested page /docs/v2/getting-started was not found on server web-03.",
 "Order A1B2C3 for 2 items, total 149.99 EUR, ships in 3-5 business days.",
 "Meeting room 4B, floor 12, building North-West Campus, capacity 18 people.",
 "const response = await fetch(`/api/v1/users/${userId}/settings?page=2&limit=50`);",
 "def compute_checksum(path: str, block_size: int = 65536) -> str:",
 "The quick brown fox jumps over 13 lazy dogs while 7 cats watch from 2 windows.",
 "Section 3.2.1 describes the ISO 8601 format; see RFC 3339 and IEEE 754 for details.",
 "Temperature 21.5 C, humidity 43%, wind 12 km/h NW, pressure 1013 hPa at 06:30.",
 "Invoice INV-2026-00417 due 30 Nov 2026; reference PO-88213, cost centre CC-1042.",
 "Package putgd_26.1112.4660-1_amd64.deb (14.2 MB) installed from the stable channel",
 "Build 1428 passed 146 of 146 tests in 154.12 s on Kubuntu 26.04 with Qt 6.10.2",
 "MacBookPro16,1 Intel Core i7-9750H 2.6GHz 6-Core 32GB DDR4 2666MHz",
 "UUID 550e8400-e29b-41d4-a716-446655440000 assigned to device VM-07.",
 "Version3BetaReleaseCandidate2ForWindowsAndLinux is the internal build name.",
 "useEffect(() => { setSelectedRowIndex(rowIndex + 1); }, [rowIndex, selectedRowIndex]);",
 "SELECT user_id, created_at FROM sessions WHERE expires_at < NOW() - INTERVAL '30 days';",
 "Chapter 12: The Lighthouse Keeper's Daughter, pages 214 to 239, 2nd edition, 1998.",
 "export PATH=$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin",
 "Monday 09:00-17:30, Saturday 10:00-14:00, closed on public holidays and 24-26 December.",
 "Scores: Team Alpha 3, Team Bravo 2, Team Charlie 0 after 90 minutes plus 4 added.",
 "kubectl get pods -n production -l app=web-frontend,tier=edge --sort-by=.metadata.name",
]
paths = {n: next(Path('/usr/share/fonts').rglob(n)) for n in FONTS}
for font in FONTS:
    for dark in (False, True):
        for size in (11, 14, 20):
            name = f'neg-{font}-{size}-{dark}'
            image = Image.new('RGB', (2200, 1400), '#202124' if dark else 'white'); draw = ImageDraw.Draw(image)
            face = ImageFont.truetype(str(paths[font]), size); y = 12; truth = []
            for line in LINES:
                draw.text((12, y), line, font=face, fill='white' if dark else 'black')
                truth.append(dict(category='clean', text_codepoints=list(map(ord, line)), box=list(draw.textbbox((12, y), line, font=face)))); y += size + 7
            image.save(out / (name + '.png')); (out / (name + '.truth.json')).write_text(json.dumps(dict(words=truth)))
