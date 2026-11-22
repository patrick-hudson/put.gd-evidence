"""Synthetic sensitive-text fixtures for #1820 acceptance, with exact token boxes.

Every value is a documented test value or generated here from a fixed seed.
Usage: fixtures.py OUTDIR WIDTH HEIGHT LOGIN
Writes OUTDIR/<id>.png and OUTDIR/truth.json.
"""
import base64
import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

MONO = '/usr/share/fonts/liberation-mono-fonts/LiberationMono-Regular.ttf'
SANS = '/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf'
NOTO = '/usr/share/fonts/google-noto/NotoSans-Regular.ttf'

rng = random.Random(1820)
ALNUM = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
GHP = 'ghp_' + ''.join(rng.choice(ALNUM) for _ in range(36))
b64 = lambda raw: base64.urlsafe_b64encode(raw).rstrip(b'=').decode()
JWT = '.'.join([b64(b'{"alg":"HS256","typ":"JWT"}'), b64(b'{"sub":"test-0001","iat":1700000000}'),
                b64(bytes(rng.randrange(256) for _ in range(32)))])
HEX64 = ''.join(rng.choice('0123456789abcdef') for _ in range(64))
AKIA = 'AKIA' + 'IOSFODNN7EXAMPLE'  # AWS documented example, split for secret scanners
SECRET = 'wJalrXUtnFEMI/K7MDENG/' + 'bPxRfiCYEXAMPLEKEY'  # AWS documented example, split
VALUES = {'ghp': GHP, 'jwt': JWT, 'hex64': HEX64, 'akia': AKIA, 'secret': SECRET}


def T(text, kind, group=None):
    return (text, kind, group)


def M(text):
    return (text, 'miss')


class Page:
    def __init__(self, fid, title, w, h, bg):
        self.fid, self.title, self.w, self.h = fid, title, w, h
        self.img = Image.new('RGB', (w, h), bg)
        self.d = ImageDraw.Draw(self.img)
        self.tokens = []
        self.lines = 0

    def rect(self, box, fill, outline=None):
        self.d.rectangle(box, fill=fill, outline=outline)

    def line(self, x, y, segments, font, size, fill):
        """segments: strings or (text, tag) pairs; tag is a kind or 'miss'."""
        f = ImageFont.truetype(font, size)
        parts = [(s, None, None) if isinstance(s, str) else (s + (None,))[:3] for s in segments]
        text = ''.join(q[0] for q in parts)
        self.d.text((x, y), text, font=f, fill=fill)
        top, bottom = self.d.textbbox((x, y), 'Ag|0', font=f)[1::2]
        lineh = bottom - top
        charw = f.getlength('0')
        # whitespace-delimited words of the drawn line, as char spans
        words, i = [], 0
        while i < len(text):
            if text[i] == ' ':
                i += 1
                continue
            j = i
            while j < len(text) and text[j] != ' ':
                j += 1
            words.append((i, j))
            i = j
        offset = 0
        for s, tag, group in parts:
            start, end = offset, offset + len(s)
            offset = end
            if tag is None:
                continue
            x0 = x + f.getlength(text[:start])
            ink = self.d.textbbox((x0, y), s, font=f)
            span = [w for w in words if w[0] < end and w[1] > start]
            wx0 = x + f.getlength(text[:span[0][0]])
            wx1 = x + f.getlength(text[:span[-1][1]])
            self.tokens.append({'kind': tag, 'text': s, 'bbox': [int(ink[0]), int(ink[1]), int(ink[2]) + 1, int(ink[3]) + 1],
                                'wordbox': [int(wx0), top, int(wx1 + .999), bottom], 'charw': round(charw, 2), 'lineh': lineh,
                                'line': self.lines, 'size': size, 'group': group})
        self.lines += 1
        return y + int(size * 1.55)

    def save(self, out):
        self.img.save(out / f'{self.fid}.png')
        return {'id': self.fid, 'title': self.title, 'size': [self.w, self.h], 'tokens': self.tokens}


def term_dark(w, h, login):
    p = Page('F01-term-dark', 'Terminal, dark theme, monospace 18 px', w, h, '#1e1e1e')
    fg, x, y, s = '#d0d0d0', 30, 30, 18
    pr = lambda: [T(login, 'name'), '@build-07:~/work$ ']
    for seg in (
        pr() + ['export AWS_ACCESS_KEY_ID=', T(AKIA, 'key')],
        pr() + ['export AWS_SECRET_ACCESS_KEY=', T(SECRET, 'key')],
        pr() + ['git remote set-url origin https://', T(GHP, 'key'), '@github.com/example/', T('acme-build-7', 'list'), '.git'],
        pr() + ['ping -c1 ', T('192.0.2.17', 'ip')],
        ['PING ', T('192.0.2.17', 'ip'), ' 56(84) bytes of data.     icmp_seq=1 ttl=64 time=0.412 ms'],
        pr() + ['ssh deploy@', T('198.51.100.23', 'ip'), '   # staging, see ', T('JIRA-4521', 'list')],
        ['Linux build-07 ', M('6.8.0-49-generic'), '  uptime ', M('12:04:31'), '  load ', M('0.42')],
        ['putgd version ', M('1.11.924'), '  package ', M('v26.1122.6198'), '  built ', M('2026-11-21')],
        pr() + ['echo $TOKEN_HEX'],
        [T(HEX64, 'key')],
        pr() + ['ls /home/', T(login, 'name'), '/Documents'],
    ):
        y = p.line(x, y, seg, MONO, s, fg)
    return p


def term_light(w, h, login):
    p = Page('F02-term-light', 'Terminal, light theme, monospace 16 px', w, h, '#fbfbf8')
    fg, x, y, s = '#202020', 30, 30, 16
    for seg in (
        ['$ cat payments-test.csv'],
        ['id,card,amount,date'],
        ['1,', T('4111111111111111', 'card'), ',19.99,', M('2026-11-21')],
        ['2,', T('5555555555554444', 'card'), ',5.00,', M('21/11/2026')],
        ['3,', T('378282246310005', 'card'), ',120.50,', M('2026-11-20')],
        ['4,', M('4111111111111112'), ',0.99,', M('2026-11-19')],
        ['$ ip -6 addr show dev eth0'],
        ['    inet6 ', T('2001:db8::8a2e:370:7334', 'ip'), '/64 scope global'],
        ['    inet6 ', T('2001:db8:85a3::42', 'ip'), '/64 scope global dynamic'],
        ['$ git log --oneline -1'],
        [M('11ddd09a7'), ' fix(capture): match each Warn kind on its own'],
        ['$ echo "contact: ', T('ops-alerts@example.com', 'email'), '"'],
    ):
        y = p.line(x, y, seg, MONO, s, fg)
    return p


def browser_form(w, h, login):
    p = Page('F03-browser-form', 'Browser checkout form, sans 20 px', w, h, '#eef1f5')
    p.rect((20, 20, w - 20, 70), '#dfe3ea')
    p.line(40, 32, ['https://shop.example.com/checkout'], SANS, 18, '#333333')
    p.rect((60, 100, 1240, 760), '#ffffff', '#c8ccd4')
    y = 120
    y = p.line(90, y, ['Payment details'], SANS, 26, '#111111')
    rows = [
        ('Card number', [T('4111 1111 1111 1111', 'card')]),
        ('Backup card', [T('5555 5555 5555 4444', 'card')]),
        ('Company Amex', [T('3782 822463 10005', 'card')]),
        ('Expired card', [M('4111 1111 1111 1112')]),
        ('Email', [T('jordan.example@example.com', 'email')]),
        ('Phone', [T('(555) 010-0123', 'phone')]),
        ('Order number', [M('ORD-88213'), '   placed ', M('2026-11-21')]),
        ('Promo code', ['WINTER25']),
    ]
    for label, value in rows:
        p.line(90, y + 12, [label], SANS, 20, '#444444')
        p.rect((330, y, 1180, y + 50), '#ffffff', '#9aa3b2')
        p.line(345, y + 12, value, SANS, 20, '#111111')
        y += 72
    return p


def chat(w, h, login):
    p = Page('F04-chat', 'Chat window with bubbles, sans 18 px', w, h, '#f3f2ef')
    p.rect((0, 0, 260, h), '#3b3f4a')
    for i, n in enumerate(('#general', '#ops', '#release', '#random')):
        p.line(24, 40 + i * 40, [n], SANS, 18, '#e0e0e0')
    msgs = [
        (False, ['Sam: my number is ', T('+1 555 010 0123', 'phone'), ' if the build breaks']),
        (True, ['You: or call the London desk ', T('+44 20 7946 0958', 'phone')]),
        (False, ['Sam: mail ', T('sam.test@example.org', 'email'), ' with the logs']),
        (True, ['You: staging box is ', T('203.0.113.42', 'ip'), ' again']),
        (False, ['Sam: ', T('Project Aurora', 'list'), ' ships after ', T('JIRA-1187', 'list')]),
        (True, ['You: the fax line ', T('555.010.0123', 'phone'), ' still works?']),
        (False, ['Sam: release ', M('v26.1122.6198'), ' on ', M('21/11/2026'), ', ticket ', M('INV-004512')]),
    ]
    y = 40
    for mine, seg in msgs:
        x = 700 if mine else 300
        p.rect((x - 14, y - 10, x + 640, y + 40), '#d7ecff' if mine else '#ffffff', '#cfd6de')
        p.line(x, y, seg, SANS, 18, '#1a1a1a')
        y += 80
    return p


def code_editor(w, h, login):
    p = Page('F05-code-editor', 'Code editor, dark, monospace 17 px', w, h, '#272822')
    p.rect((0, 0, 56, h), '#202020')
    lines = [
        ('#75715e', ['# settings for the ', T('acme-build-7', 'list'), ' pipeline (', T('JIRA-2210', 'list'), ')']),
        ('#f8f8f2', ['AWS_KEY = "', T(AKIA, 'key'), '"']),
        ('#f8f8f2', ['GITHUB_TOKEN = "', T(GHP, 'key'), '"']),
        ('#f8f8f2', ['SESSION = "', T(JWT, 'key'), '"']),
        ('#f8f8f2', ['SIGNING_HEX = "', T(HEX64, 'key'), '"']),
        ('#e6db74', ['OWNER = "', T('ops-alerts@example.com', 'email'), '"']),
        ('#ae81ff', ['VERSION = "', M('1.11.924'), '"   # released ', M('2026-11-21')]),
        ('#ae81ff', ['BUILD_ID = ', M('26112261980042')]),
        ('#f8f8f2', ['HOSTS = ["', T('192.0.2.88', 'ip'), '", "', T('2001:db8::1:2', 'ip'), '"]']),
        ('#75715e', ['# commit ', M('522750745de595b09cf1'), ' by ', T(login, 'name')]),
    ]
    y = 30
    for n, (col, seg) in enumerate(lines, 1):
        p.line(12, y, [str(n)], MONO, 15, '#75715e')
        y = p.line(76, y, seg, MONO, 17, col)
    return p


def spreadsheet(w, h, login):
    p = Page('F06-spreadsheet', 'Spreadsheet-like table, sans 15 px', w, h, '#ffffff')
    cols = [40, 230, 520, 720, 900, 1170]
    head = ['Name', 'Email', 'Phone', 'IP', 'Card', 'Notes']
    rows = [
        ['Ada Example', T('ada@example.com', 'email'), T('555.010.0123', 'phone'), T('198.51.100.7', 'ip'), T('5555-5555-5555-4444', 'card'), 'renewal'],
        ['Ben Sample', T('ben@example.org', 'email'), T('(555) 010-0123', 'phone'), T('203.0.113.9', 'ip'), T('3782-822463-10005', 'card'), 'VIP'],
        ['Cy Test', T('cy.test@example.com', 'email'), T('+1 555 010 0123', 'phone'), T('192.0.2.200', 'ip'), T('4111-1111-1111-1111', 'card'), 'net 30'],
        ['Order', M('ORD-2026-0042'), M('21/11/2026'), M('1.11.924'), M('5555-5555-5555-4445'), 'hold'],
    ]
    y = 40
    p.rect((30, y - 8, 1260, y + 26), '#e8eef7')
    for c, t in zip(cols, head):
        p.line(c, y, [t], SANS, 15, '#000000')
    y += 40
    for r in rows:
        for c, t in zip(cols, r):
            p.line(c, y, [t], SANS, 15, '#111111')
        p.d.line((30, y + 26, 1260, y + 26), fill='#d0d0d0')
        y += 40
    for c in cols[1:]:
        p.d.line((c - 10, 32, c - 10, y - 14), fill='#d0d0d0')
    return p


def small_font(w, h, login):
    p = Page('F07-small-font', 'Small fonts: sans 11 px and monospace 10 px', w, h, '#ffffff')
    y = 30
    for seg, font, s in (
        (['Card on file ', T('4111 1111 1111 1111', 'card'), ' exp 11/28'], SANS, 11),
        (['Contact ', T('jordan.example@example.com', 'email'), ' or ', T('(555) 010-0123', 'phone')], SANS, 11),
        (['key=', T(AKIA, 'key'), ' region=eu-west-1'], MONO, 10),
        (['server ', T('192.0.2.17', 'ip'), ' build ', M('1.11.924')], MONO, 10),
        (['Card on file ', T('5555 5555 5555 4444', 'card'), ' (13 px)'], SANS, 13),
    ):
        y = p.line(40, y, seg, font, s, '#222222')
        y += 6
    return p


def large_font(w, h, login):
    p = Page('F08-large-font', 'Large fonts, sans 44 px', w, h, '#fafafa')
    y = 60
    for seg in (
        ['Card ', T('4111 1111 1111 1111', 'card')],
        ['Mail ', T('sam.test@example.org', 'email')],
        ['Host ', T('203.0.113.42', 'ip')],
        ['Ver ', M('v26.1122.6198')],
    ):
        y = p.line(60, y, seg, SANS, 44, '#101010') + 20
    return p


def low_contrast(w, h, login):
    p = Page('F09-low-contrast', 'Low-contrast text on grey and on dark', w, h, '#9c9c9c')
    y = 50
    for seg, col in (
        (['Card ', T('4111 1111 1111 1111', 'card')], '#7a7a7a'),
        (['Email ', T('jordan.example@example.com', 'email')], '#808080'),
        (['Key ', T(AKIA, 'key')], '#848484'),
    ):
        y = p.line(60, y, seg, SANS, 22, col) + 10
    p.rect((0, 400, w, h), '#2a2a2a')
    y = 440
    for seg, col in (
        (['Card ', T('5555 5555 5555 4444', 'card')], '#444444'),
        (['Phone ', T('+44 20 7946 0958', 'phone')], '#4a4a4a'),
        (['IP ', T('198.51.100.23', 'ip')], '#505050'),
    ):
        y = p.line(60, y, seg, SANS, 22, col) + 10
    return p


def edges(w, h, login):
    p = Page('F10-edges', 'Matches touching the image edges, sans 20 px', w, h, '#ffffff')
    f = ImageFont.truetype(SANS, 20)
    def at(x, y, seg):
        p.line(x, y, seg, SANS, 20, '#111111')
    at(1, 0, [T('ada@example.com', 'email')])
    cw = int(f.getlength('4111 1111 1111 1111'))
    at(w - cw - 2, 0, [T('4111 1111 1111 1111', 'card')])
    at(1, h - 25, [T('+1 555 010 0123', 'phone')])
    iw = int(f.getlength('203.0.113.42'))
    at(w - iw - 2, h - 25, [T('203.0.113.42', 'ip')])
    at(1, h // 2, [T(AKIA, 'key')])
    at(w // 2 - 100, h // 2, ['middle text ', M('2026-11-21')])
    return p


def multi(w, h, login):
    p = Page('F11-multi-across', 'Several matches per line and matches across lines, sans 19 px', w, h, '#ffffff')
    y = 40
    y = p.line(40, y, ['To: ', T('a.one@example.com', 'email'), ', ', T('b.two@example.org', 'email'), ', ', T('c.three@example.com', 'email'),
                       ' hosts ', T('192.0.2.1', 'ip'), ' ', T('192.0.2.2', 'ip'), ' ', T('198.51.100.3', 'ip')], SANS, 19, '#111111')
    y = p.line(40, y, ['Cards ', T('4111 1111 1111 1111', 'card'), ' and ', T('5555 5555 5555 4444', 'card'), ' and ', T('378282246310005', 'card')], SANS, 19, '#111111')
    y = p.line(40, y, ['Keys ', T(AKIA, 'key'), '  ', T(GHP, 'key')], SANS, 19, '#111111')
    y += 30
    # a card number wrapped across two lines, and an email wrapped at the @
    y = p.line(40, y, ['The card we charged was ', T('4111 1111', 'card', 'w1')], SANS, 19, '#111111')
    y = p.line(40, y, [T('1111 1111', 'card', 'w1'), ' yesterday at noon.'], SANS, 19, '#111111')
    y += 30
    y = p.line(40, y, ['Please reply to ', T('jordan.example@', 'email', 'w2')], SANS, 19, '#111111')
    y = p.line(40, y, [T('example.com', 'email', 'w2'), ' before Friday.'], SANS, 19, '#111111')
    y += 30
    y = p.line(40, y, ['Call ', T('+1 555', 'phone', 'w3')], SANS, 19, '#111111')
    y = p.line(40, y, [T('010 0123', 'phone', 'w3'), ' after six.'], SANS, 19, '#111111')
    return p


def near_only(w, h, login):
    p = Page('F12-near-misses', 'Near misses only: nothing here should be covered', w, h, '#ffffff')
    y = 40
    for seg in (
        ['Invalid card ', M('4111 1111 1111 1112'), ' and ', M('5555-5555-5555-4445'), ' and ', M('3782 822463 10006')],
        ['Dates ', M('2026-11-21'), ', ', M('21/11/2026'), ', ', M('11/21/2026')],
        ['Versions ', M('1.11.924'), ', ', M('v26.1122.6198'), ', ', M('6.8.0-49')],
        ['Orders ', M('ORD-88213'), ', ', M('INV-004512'), ', ', M('PO 4471-22')],
        ['Ordinary words: the quick brown fox jumps over the lazy dog'],
        ['Short hash ', M('11ddd09a7'), ' and a time ', M('12:04:31')],
    ):
        y = p.line(40, y, seg, SANS, 20, '#111111') + 8
    return p


def list_name(w, h, login):
    p = Page('F13-list-name', 'Saved list words, custom pattern, login and name', w, h, '#f7f7ff')
    y = 40
    for seg in (
        ['Status of ', T('Project Aurora', 'list'), ' and the ', T('acme-build-7', 'list'), ' runner'],
        ['Tickets ', T('JIRA-4521', 'list'), ', ', T('JIRA-1187', 'list'), ' and ', M('JIRAX-99'), ' (not a ticket)'],
        ['Signed in as ', T(login, 'name'), ' on build-07'],
        ['Home folder /home/', T(login, 'name'), '/work'],
        ['Unrelated: project aurora-borealis photos, acme build seven'],
    ):
        y = p.line(40, y, seg, SANS, 20, '#111111') + 8
    return p


def dense(w, h, login):
    p = Page('F14-dense', 'Dense full screen of 9 px text, for the recognition limit', w, h, '#ffffff')
    f = 9
    words = 'lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor'.split()
    y = 2
    n = 0
    while y < h - 12:
        seg = []
        x_words = []
        for i in range(34):
            x_words.append(words[(n + i) % len(words)])
        n += 7
        line = ' '.join(x_words)
        if (y // 11) % 9 == 4:
            seg = [line[:60] + ' ', T('4111 1111 1111 1111', 'card'), ' ' + line[60:200]]
        else:
            seg = [line * 2]
        p.line(2, y, seg, MONO, f, '#000000')
        y += 11
    return p


BUILDERS = [term_dark, term_light, browser_form, chat, code_editor, spreadsheet, small_font, large_font,
            low_contrast, edges, multi, near_only, list_name, dense]


def main():
    out, w, h, login = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    out.mkdir(parents=True, exist_ok=True)
    truth = {'values': VALUES, 'size': [w, h], 'login': login, 'fixtures': [b(w, h, login).save(out) for b in BUILDERS]}
    (out / 'truth.json').write_text(json.dumps(truth, indent=1))
    for f in truth['fixtures']:
        kinds = {}
        seen = set()
        for t in f['tokens']:
            if t['group'] and t['group'] in seen:
                continue
            seen.add(t['group'])
            kinds[t['kind']] = kinds.get(t['kind'], 0) + 1
        print(f['id'], kinds)


if __name__ == '__main__':
    main()
