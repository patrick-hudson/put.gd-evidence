# collect7.py PREFIX : one JSON object per run of a campaign (for the table), from result.json, verification.json, helper.log
import sys, json, re, collections
from pathlib import Path
P = Path.home() / 'work/sf7'
out = []
for d in sorted((P / 'runs').glob(sys.argv[1] + '-*')):
    if not d.is_dir():
        continue
    r = json.loads((d / 'result.json').read_text()) if (d / 'result.json').exists() else {}
    c = r.get('capture') or {}
    v = json.loads((d / 'verification.json').read_text()) if (d / 'verification.json').exists() else {}
    log = (d / 'helper.log').read_text(errors='replace') if (d / 'helper.log').exists() else ''
    st = collections.Counter(re.findall(r'scroll step: (\w+)', log))
    top = re.findall(r'way to the top (\d+) steps, (\d+) ms, ([^\n(]*)', log)
    out.append({'name': d.name, 'site': r.get('site'), 'browser': r.get('browser'), 'mode': r.get('mode'), 'rect': r.get('rect'),
                'end': c.get('endReason'), 'height': c.get('height'), 'truncated': c.get('truncated'), 'note': c.get('note'), 'topReached': c.get('topReached'),
                'docBefore': (r.get('before') or {}).get('docHeight'), 'docAfter': (r.get('after') or {}).get('docHeight'), 'viewportRows': (r.get('before') or {}).get('h'),
                'seconds': r.get('seconds'), 'failed': r.get('failed'), 'referenceError': r.get('referenceError'),
                'bands': v.get('bands'), 'exactBands': v.get('exactBands'), 'shiftedBands': v.get('shiftedBands'), 'badBands': v.get('badBands'), 'bad': v.get('bad'), 'shiftChanges': v.get('shiftChanges'),
                'excluded': [e.get('why') for e in (v.get('excluded') or [])], 'steps': dict(st), 'lowConfidence': log.count('low-confidence'),
                'wayToTop': top[-1] if top else None, 'sha256': c.get('sha256'), 'operationId': (r.get('state') or {}).get('operationId')})
print(json.dumps(out))
