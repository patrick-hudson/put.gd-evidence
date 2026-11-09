#!/usr/bin/env python3
import glob, json, re, statistics as st, sys, os
out = {}
for tag in sys.argv[1:]:
    rows = {'hw': [], 'sw': []}
    for f in sorted(glob.glob(tag + '/r[0-9]*.json')):
        d = json.load(open(f)); x = d['rounds'][-1]; mode = f.rsplit('-',1)[1].split('.')[0]
        if x.get('error'): rows[mode].append({'run': os.path.basename(f), 'error': x['error']}); continue
        c = x['clips']['working']; t = x['ticks']; r = x['recorder']; fr = r.get('frames:', '')
        m = re.search(r'(\d+) reached the video encoder, (\d+) leaked at the capture queue; source arrivals (\d+)', fr)
        m2 = re.search(r'contents (\d+) new / (\d+) same dropped, cadence lock (\d+) early', fr)
        p = x.get('progress') or {}
        rows[mode].append(dict(run=os.path.basename(f)[:-5], distinctFps=c['distinctPerSecond'], frames=c['frames'], repeats=c['pairs']['repeat'], skip1=c['pairs']['skip1'], skip2plus=c['pairs']['skip2plus'],
            longestStallMs=c['longestStallMs'], leakedAtCaptureQueue=int(m.group(2)), recorderFramesDropped=p.get('framesDropped'), framesEncodedProgress=p.get('framesEncoded'), sourceArrivals=int(m.group(3)), newContents=int(m2.group(1)), earlyDropped=int(m2.group(3)),
            fixtureFps=round(1000/t['meanMs'],2), fixtureMissed=t['missedFrames'], fluidFraction=c['fluidFraction'], encoder=r['started with'].split(' ')[0], machineBusy=x['machineBusy'], recorderCpuMs=x['cpuMs']['recorder'], compositorCpuMs=x['cpuMs']['compositor']))
    out[tag] = rows
    print('==', tag)
    for mode, rs in rows.items():
        good = [r for r in rs if 'error' not in r]
        print(mode, 'n=%d err=%d' % (len(good), len(rs)-len(good)))
        for r in rs: print('  ', r.get('run'), r.get('error') or ' '.join(str(r[k]) for k in ('distinctFps','repeats','skip1','longestStallMs','leakedAtCaptureQueue','recorderFramesDropped','sourceArrivals','earlyDropped','fixtureFps','fixtureMissed','encoder')))
        for k in ('distinctFps','repeats','skip1','longestStallMs','leakedAtCaptureQueue','sourceArrivals','earlyDropped','fixtureFps','fixtureMissed','recorderCpuMs'):
            v=[r[k] for r in good if r[k] is not None]
            print('   %-22s median %-9.2f min %-9.2f max %-9.2f spread %.2f' % (k, st.median(v), min(v), max(v), max(v)-min(v)))
json.dump(out, open('combined.json','w'), indent=1)
