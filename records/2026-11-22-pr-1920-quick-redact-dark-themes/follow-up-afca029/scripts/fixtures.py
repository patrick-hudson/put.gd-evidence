"""Generate synthetic fixtures inside a private builder directory."""
import base64
import html
import json
import random
import string
import sys
from pathlib import Path

THEMES = {
    'solarized': ('002b36', '839496', '586e75', '2aa198'),
    'github': ('0d1117', 'c9d1d9', '6e7681', 'a5d6ff'),
    'monokai': ('272822', 'f8f8f2', '75715e', 'e6db74'),
}
MARK = 'e75397'
COLUMN = 25

def generate(root, seed):
    rnd = random.Random(seed)
    def body(n, chars=string.ascii_letters + string.digits):
        return ''.join(rnd.choices(chars, k=n))
    def segment(data):
        return base64.urlsafe_b64encode(data).decode().rstrip('=')
    def pat():
        return 'github' + '_pat_' + body(22) + '_' + body(59)
    jwt = '.'.join([segment(b'{"alg":"HS256","typ":"JWT"}'),
                    segment(json.dumps({'sub': body(8)}).encode()),
                    body(43, string.ascii_letters + string.digits + '-_')])
    sha = body(40, string.hexdigits[:16])
    uuid = '-'.join(body(n, string.hexdigits[:16]) for n in (8, 4, 4, 4, 12))
    rows = [
        ('GITHUB_CLASSIC=', 'gh' + 'p_' + body(36), 'key'),
        ('GITHUB_FINE_GRAINED=', pat(), 'key'),
        ('OPENAI_API_KEY=', 'sk-' + 'proj-' + body(60), 'key'),
        ('SLACK_BOT_TOKEN=', 'xo' + 'xb-' + body(12, string.digits) + '-' + body(12, string.digits) + '-' + body(24), 'key'),
        ('GITLAB_ACCESS=', 'gl' + 'pat-' + body(20), 'key'),
        ('AWS_ACCESS_KEY_ID=', 'AK' + 'IA' + body(16, string.ascii_uppercase + string.digits), 'key'),
        ('AWS_SECRET_ACCESS_KEY=', body(40, string.ascii_letters + string.digits + '+/'), 'key'),
        ('STRIPE_SECRET=', 'sk_' + 'live_' + body(32), 'key'),
        ('ID_TOKEN=', jwt, 'key'),
        ('# old:', pat(), 'comment'),
        ('BUILD_GIT_SHA=', sha, 'decoy'),
        ('DEPLOYMENT_ID=', uuid, 'decoy'),
        ('DEPLOYMENT_ENV=', 'staging', 'other'),
    ]
    root.mkdir(exist_ok=True)
    (root / 'rows.json').write_text(json.dumps([[label, len(value), kind] for label, value, kind in rows]))
    for name, (bg, fg, comment, string_colour) in THEMES.items():
        def col(code):
            return '\x1b[38;2;' + ';'.join(str(int(code[i:i+2], 16)) for i in (0, 2, 4)) + 'm'
        terminal = ['QR LAB 1920'.ljust(COLUMN) + col(MARK) + 'MMMMMM\x1b[0m']
        markup = ['<div>QR LAB 1920'.ljust(5+COLUMN) + '<i>MMMMMM</i></div>']
        for label, value, kind in rows:
            ansi = col(comment) if kind == 'comment' else ''
            terminal.append(ansi + label.ljust(COLUMN) + value + '\x1b[0m')
            colour = comment if kind == 'comment' else string_colour
            markup.append(f'<div style="color:#{comment if kind == "comment" else fg}">'
                          + html.escape(label.ljust(COLUMN))
                          + f'<span style="color:#{colour}">' + html.escape(value) + '</span></div>')
        terminal.append('END FIXTURE'.ljust(COLUMN) + col(MARK) + 'MMMMMM\x1b[0m')
        markup.append('<div>END FIXTURE'.ljust(5+COLUMN) + '<i>MMMMMM</i></div>')
        (root / f'{name}.txt').write_text('\r\n'.join(terminal))
        page = (
            f'<!doctype html><meta charset="utf-8"><title>Quick redact lab fixture</title>'
            f'<style>html{{background:#{bg};color:#{fg}}}body{{margin:48px;font:13px/21px "DejaVu Sans Mono",monospace;'
            'font-variant-ligatures:none;white-space:pre}div{height:21px}i{font-style:normal;color:#' + MARK + '}</style>'
            '<main>' + ''.join(markup) + '</main>')
        (root / f'{name}.html').write_text(page)
        if name == 'github':
            blurred = page.replace('</style>', 'span{filter:blur(.8px)}</style>')
            (root / f'{name}-blur.html').write_text(blurred)
    return rows

def whole_screen(root, token, name='', font_px=21, ink='#424854', equal_background=False, bright='#b5c2d4'):
    from PIL import Image, ImageDraw, ImageFont
    canvas = Image.new('RGB', (3840, 2160), '#282c34' if equal_background else '#13151a')
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', font_px)
    panel = (120, 168, 1790, 1100)
    step = font_px + (11 if name else 10)
    lines = ['[deployment]', 'region = "us-east-1"', 'name = "redaction-fixture"',
             'environment = "staging"', 'rollback = true', 'workers = 4',
             'service = "test-only"', 'port = 8080', 'integrations = []']
    for x, y, w, h in (panel, (2070, 168, 1620, 660), (2070, 960, 1620, 660)):
        draw.rectangle((x, y, x+w-1, y+h-1), fill='#282c34', outline='#20242e' if equal_background else None, width=2)
        for i, line in enumerate(lines):
            draw.text((x+46, y+42+i*step), line, font=font, fill=bright)
    x, y, w, h = panel
    lead = '# retired: '
    at = (x+46, y+42+(len(lines)+bool(name))*step)
    draw.text(at, lead+token, font=font, fill=ink)
    token_at = (at[0]+round(draw.textlength(lead, font=font)), at[1])
    box = draw.textbbox(token_at, token, font=font)
    crop = (x, y, x+w, at[1]+font_px+50 if name else y+h)
    canvas.save(root / f'whole{name}.png')
    canvas.crop(crop).save(root / f'crop{name}.png')
    box_file = root / 'file-boxes.json'
    boxes = json.loads(box_file.read_text()) if box_file.exists() else {}
    boxes.update({f'whole{name}': box, f'crop{name}': [box[0]-x, box[1]-y, box[2]-x, box[3]-y]})
    box_file.write_text(json.dumps(boxes))

if __name__ == '__main__':
    directory = Path(sys.argv[1])
    fixture_rows = generate(directory, int(sys.argv[2]))
    whole_screen(directory, fixture_rows[9][1])
