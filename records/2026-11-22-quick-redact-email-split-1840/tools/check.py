"""Check a redacted capture of the #1838 fixture against its word masks.
Usage: check.py FIXTURE_DIR RESULT.png [OFFSET_X OFFSET_Y]
For every word: matched ink pixels not black (leaked), and neighbour ink
pixels changed (covered). A pixel counts as covered when it differs from the
fixture by more than 8 in any channel; a matched pixel counts as hidden only
when it is black (each channel 8 or less). Prints JSON."""
import json
import sys
from pathlib import Path

from PIL import Image


def main():
    fixture = Path(sys.argv[1])
    result = Image.open(sys.argv[2]).convert('RGB')
    dx, dy = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, 0)
    page = Image.open(fixture / 'fixture.png').convert('RGB')
    labels = Image.open(fixture / 'labels.png')
    words = json.loads((fixture / 'words.json').read_text())
    lab = labels.load()
    src = page.load()
    got = result.load()
    out = []
    for word in words:
        x0, y0, x1, y1 = word['box']
        ink = shown = changed = 0
        for y in range(y0, y1):
            for x in range(x0, x1):
                if lab[x, y] != word['n']:
                    continue
                ink += 1
                rx, ry = x - dx, y - dy
                if not (0 <= rx < result.width and 0 <= ry < result.height):
                    continue
                a, b = src[x, y], got[rx, ry]
                if max(b) > 8:
                    shown += 1
                if max(abs(p - q) for p, q in zip(a, b)) > 8:
                    changed += 1
        out.append({**word, 'ink': ink, 'shown': shown, 'changed': changed})
    matched = [w for w in out if w['role'] == 'matched']
    neighbours = [w for w in out if w['role'] == 'neighbour']
    summary = {
        'matchedWords': len(matched),
        'matchedWordsWithInkShowing': [f"{w['block']}:{w['text']}:{w['shown']}" for w in matched if w['shown']],
        'matchedWordsFullyHidden': sum(1 for w in matched if not w['shown']),
        'neighbourWords': len(neighbours),
        'neighbourWordsTouched': [f"{w['block']}:{w['text']}:{w['changed']}/{w['ink']}" for w in neighbours if w['changed']],
        'takenByFind': [f"{w['block']}:{w['text']}:{w['changed']}/{w['ink']}" for w in out if w['role'] == 'taken-by-find' and w['changed']],
    }
    print(json.dumps({'summary': summary, 'words': out}, indent=1))


main()
