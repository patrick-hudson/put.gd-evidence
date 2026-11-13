"""Realistic-token variant of tools/lab/text_corpus/generate.py's sensitive() pages
(same fonts, sizes, layout); seeded random tokens instead of repeated letters.
Throwaway, never committed; every value is made up."""
import base64, hashlib, json, random, string, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
FONTS = ('DejaVuSans.ttf', 'DejaVuSerif.ttf', 'DejaVuSansMono.ttf', 'LiberationSans-Regular.ttf')
def card(prefix='999999000000000'):
    for last in range(10):
        v = prefix + str(last); d = list(map(int, v[::-1]))
        if sum(x if i % 2 == 0 else (2*x if x < 5 else 2*x-9) for i, x in enumerate(d)) % 10 == 0: return v
def items(seed):
    r = random.Random(seed); A = string.ascii_letters + string.digits
    rnd = lambda alphabet, n: ''.join(r.choice(alphabet) for _ in range(n))
    b64 = lambda n: base64.b64encode(bytes(r.randrange(256) for _ in range(n))).decode()
    url = lambda b: base64.urlsafe_b64encode(b).decode().rstrip('=')
    jwt = '.'.join([url(b'{"alg":"HS256","typ":"JWT"}'), url(json.dumps({'sub': rnd(string.digits, 10), 'name': 'Synthetic', 'iat': r.randrange(10**9, 2*10**9)}).encode()), url(bytes(r.randrange(256) for _ in range(32)))])
    pem = '-----BEGIN ' + 'PRIVATE KEY-----\n' + '\n'.join(b64(48) for _ in range(3)) + '\n-----END PRIVATE KEY-----'
    return [('email', 'corpus@example.invalid'), ('phone', '+1 202 555 0142'), ('phone', '020 7946 0958'),
            ('address', '192.0.2.42'), ('address', '2001:db8::42'), ('card', card()),
            ('token', 'AK' + 'IA' + rnd(string.ascii_uppercase + '234567', 16)), ('token', 'gh' + 'p_' + rnd(A, 36)),
            ('token', 'gl' + 'pat-' + rnd(A + '_-', 20)), ('token', 'xo' + 'xb-' + rnd(string.digits, 12) + '-' + rnd(string.digits, 12) + '-' + rnd(A, 24)),
            ('token', 'sk_' + 'test_' + rnd(A, 24)), ('token', jwt), ('token', pem),
            ('token', hashlib.sha256(rnd(A, 20).encode()).hexdigest()), ('token', b64(33))]
paths = {n: next(Path('/usr/share/fonts').rglob(n)) for n in FONTS}
k = 0
for font in FONTS:
    for dark in (False, True):
        for size in (11, 14, 20):
            k += 1; name = f'real-{font}-{size}-{dark}'
            image = Image.new('RGB', (2200, 1400), '#202124' if dark else 'white'); draw = ImageDraw.Draw(image)
            face = ImageFont.truetype(str(paths[font]), size); y = 12; truth = []
            for category, text in items(1000 + k):
                for line in text.split('\n'):
                    box = draw.textbbox((12, y), line, font=face)
                    draw.text((12, y), line, font=face, fill='white' if dark else 'black')
                    truth.append(dict(category=category, text_codepoints=list(map(ord, line)), box=list(box))); y += size + 7
            image.save(out / (name + '.png'))
            (out / (name + '.truth.json')).write_text(json.dumps(dict(words=truth, font=font, font_pixels=size)))
print(k, 'pages')
