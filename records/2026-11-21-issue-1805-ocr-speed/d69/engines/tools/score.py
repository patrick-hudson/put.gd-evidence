"""Summarize a bench2 run: per class, 1080p screens, the two GNOME 4K screens, CER vs hand truth,
CER vs today's helper (reference rows), bag-of-words F1, engine-only figures. python3 -I score.py MANIFEST RUN [REF]"""
import json, sys, statistics, collections, unicodedata, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from bench2 import rates, normalize
man = Path(sys.argv[1]); run = Path(sys.argv[2]); ref = Path(sys.argv[3]) if len(sys.argv) > 3 else None
caps = {c['id']: c for c in json.loads(man.read_text())['captures']}
rows = [r for r in json.loads((run / 'rows.json').read_text()) if r['status'] == 'ok']
refrows = {r['id']: r for r in json.loads((ref / 'rows.json').read_text())} if ref else {}
def bow(t):
    return collections.Counter(normalize(t).split())
def f1(truth, out):
    a, b = bow(truth), bow(out)
    inter = sum((a & b).values()); p = inter / max(1, sum(b.values())); r = inter / max(1, sum(a.values()))
    return 2 * p * r / max(1e-9, p + r)
for r in rows:
    truth = (man.parent / caps[r['id']]['transcript']).read_text(encoding='utf-8')
    r['f1'] = f1(truth, r['text'])
    if r['id'] in refrows and 'text' in refrows[r['id']]:
        r['cvt'] = rates(refrows[r['id']]['text'], r['text'])[0]
        r['ref_wall'] = refrows[r['id']]['wall']; r['ref_cer'] = refrows[r['id']]['cer']
def med(x):
    return round(statistics.median(x), 4) if x else None
def grp(g):
    if not g: return None
    ch = sum(r['chars'] for r in g)
    d = dict(n=len(g), wall_sum=round(sum(r['wall'] for r in g), 2), cpu_sum=round(sum(r['cpu'] for r in g), 2),
             wall_p50=med([r['wall'] for r in g]), wall_max=round(max(r['wall'] for r in g), 3),
             rss_max_MiB=round(max(r['maxrssKiB'] for r in g) / 1024, 1), rss_p50_MiB=round(med([r['maxrssKiB'] for r in g]) / 1024, 1),
             cer_med=med([r['cer'] for r in g]), cer_pooled=round(sum(r['cer'] * r['chars'] for r in g) / ch, 4),
             wer_mean=round(sum(r['wer'] for r in g) / len(g), 4), bowF1_mean=round(sum(r['f1'] for r in g) / len(g), 4))
    if any('engineMs' in r for r in g):
        d.update(engine_s_sum=round(sum(r.get('engineMs', 0) for r in g) / 1000, 2), engine_p50_ms=med([r.get('engineMs', 0) for r in g]),
                 load_p50_ms=med([r.get('loadMs', 0) for r in g]), import_p50_ms=med([r.get('importMs', 0) for r in g]),
                 engine_only_max_MiB=round(max(r.get('engineOnlyKiB', 0) for r in g) / 1024, 1),
                 engine_only_p50_MiB=round(med([r.get('engineOnlyKiB', 0) for r in g]) / 1024, 1),
                 base_py_MiB=round(med([r.get('baseKiB', 0) for r in g]) / 1024, 1))
    if any('detMs' in r for r in g):
        d.update(det_s_sum=round(sum(r.get('detMs', 0) for r in g) / 1000, 2), rec_s_sum=round(sum(r.get('recMs', 0) for r in g) / 1000, 2))
    if any('above128Ms' in r for r in g):
        d.update(above128_ms_max=max(r.get('above128Ms', 0) for r in g), above128_ms_sum=sum(r.get('above128Ms', 0) for r in g))
    rr = [r for r in g if 'cvt' in r]
    if rr:
        d.update(cer_vs_today_med=med([r['cvt'] for r in rr]),
                 cer_vs_today_pooled=round(sum(r['cvt'] * r['chars'] for r in rr) / sum(r['chars'] for r in rr), 4),
                 today_wall_sum=round(sum(r['ref_wall'] for r in rr), 2),
                 today_cer_pooled=round(sum(r['ref_cer'] * r['chars'] for r in rr) / sum(r['chars'] for r in rr), 4))
    return d
is4k = lambda r: r['id'].startswith('gnome4k')
dims = lambda r: caps[r['id']].get('dimensions') or [0, 0]
s1080 = lambda r: r['cls'] == 'monitor' and not is4k(r) and dims(r)[0] <= 1920
out = dict(run=str(run), all=grp(rows), screens_1080p=grp([r for r in rows if s1080(r)]),
           screens_m74_125=grp([r for r in rows if r['cls'] == 'monitor' and dims(r)[0] == 3072]),
           gnome_4k=grp([r for r in rows if is4k(r)]), regions=grp([r for r in rows if r['cls'] != 'monitor']),
           classes={c: grp([r for r in rows if r['cls'] == c]) for c in sorted({r['cls'] for r in rows})},
           worst=sorted(((round(r['cer'], 3), r['id']) for r in rows), reverse=True)[:8])
print(json.dumps(out, indent=1))
