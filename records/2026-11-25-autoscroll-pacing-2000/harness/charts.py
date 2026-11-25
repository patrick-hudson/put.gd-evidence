import sys, re, datetime
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D = Path(sys.argv[1])
NIGHT, FIX = '#b4483c', '#2f6db5'

# 1. Session test: Sol's #2000 case.
txt = (D / 'session-steps.txt').read_text().splitlines()
runs, who = {}, None
for i, l in enumerate(txt):
    if l.startswith('== '): who = l[3:]
    if l.startswith('stall=3500'):
        steps = [tuple(map(int, s.split(':'))) for s in txt[i + 1].split()]
        runs[who] = steps
fig, ax = plt.subplots(figsize=(11, 4.6), dpi=130)
cum = {}
for name, color, label in (('base', NIGHT, 'nightly 26.1124.6905 (session code as on nightly)'), ('fix', FIX, 'this PR (8ad80f46 / 6150e8ad)')):
    t = [s[0] / 1000 for s in runs[name]]; n = [s[1] for s in runs[name]]
    ax.step(t, n, where='post', color=color, lw=2.2, label=f'{label}: {len(n)} steps')
    ax.plot(t, n, 'o', color=color, ms=3.5)
ax.set_xlabel('capture time (s, fake clock)'); ax.set_ylabel('notches in the step')
ax.set_ylim(0, 5.2); ax.set_yticks(range(0, 6))
ax.axvspan(0.7, 4.2, color='#999', alpha=0.15)
ax.text(2.45, 4.75, '3.5 s stall:\nfirst step runs out\nof time unmeasured', ha='center', va='top', fontsize=9)
ax.annotate('nightly: never measures again,\n1 notch a step to the end (78 steps, 32.3 s, 0 px/notch)', xy=(20, 1), xytext=(17, 2.0), color=NIGHT, fontsize=10, weight='bold',
            arrowprops=dict(arrowstyle='->', color=NIGHT))
ax.annotate('fix: step 2 takes a fresh frame that proves the rest,\nstep 3 measures 40 px/notch, then 4 notches a step\n(25 steps, 19.2 s)', xy=(4.85, 4), xytext=(11.5, 3.3), color=FIX, fontsize=10, weight='bold',
            arrowprops=dict(arrowstyle='->', color=FIX))
ax.set_title('#2000 — session test, damage-only stream, 40 px a notch, 3.5 s stall in the first step (Sol\'s d69 case)', fontsize=11)
ax.annotate('end of the page:\nshort last steps', xy=(11.0, 1), xytext=(11.6, 0.35), color=FIX, fontsize=8.5)
ax.legend(loc='upper right', fontsize=9); ax.grid(alpha=.25)
fig.tight_layout(); fig.savefig(D / '1-session-steps-before-after.png')

# 2. Live f44 GNOME, Firefox.
live = {}
for l in (D / 'live-steps.txt').read_text().splitlines():
    r, p, *steps = l.split()
    pts = []
    t0 = None
    for s in steps:
        ts, n = s.split('|')
        t = datetime.datetime.strptime(ts, '%H:%M:%S.%f')
        t0 = t0 or t
        pts.append(((t - t0).total_seconds(), int(n)))
    live[(r, p)] = pts
meta = {'creep': 'creep page (keeps moving 3.5 s after the first notch)', 'wiki': 'en.wikipedia.org/wiki/Linux'}
res = {('nfr', 'creep'): '24,994 rows = page, end_of_content, 48.2 s', ('pfr', 'creep'): '24,994 rows = page, end_of_content, 49.2 s',
       ('nfr', 'wiki'): '24,094 rows = page, end_of_content, 43.0 s', ('pfr', 'wiki'): '24,094 rows = page, end_of_content, 50.0 s'}
fig, axs = plt.subplots(2, 1, figsize=(11, 7.4), dpi=130, sharey=True)
for ax, p in zip(axs, ('creep', 'wiki')):
    for r, color, label in (('nfr', NIGHT, 'nightly 26.1124.6905'), ('pfr', FIX, 'PR 26.1125.6942 (8ad80f46)')):
        pts = live[(r, p)]
        ax.step([a for a, _ in pts], [b for _, b in pts], where='post', color=color, lw=1.8, label=f'{label}: {len(pts)} steps; {res[(r, p)]}')
    ax.set_title(f'f44 GNOME 50 Wayland, Firefox 158 (wheel 35%), {meta[p]}', fontsize=10.5)
    ax.set_ylabel('notches in the step'); ax.grid(alpha=.25); ax.legend(loc='center right', bbox_to_anchor=(1.0, 0.42), fontsize=8.5)
    ax.set_ylim(0, 13.5)
axs[1].set_xlabel('seconds since the first step')
axs[0].annotate('both builds: 1-notch steps until the creep stops,\nthen measured (progress event 41 vs 42)', xy=(3.5, 1), xytext=(6, 6.5), fontsize=9.5,
                arrowprops=dict(arrowstyle='->'))
axs[1].annotate('later step sizes follow Firefox\'s own wheel\nacceleration (px/notch 23 to 31 on nightly,\n23 to 39 on the PR);\nno fresh frame after the first on either build', xy=(22, 9.6), xytext=(1.5, 2.0), fontsize=9.5,
                arrowprops=dict(arrowstyle='->'))
fig.suptitle('#2000 live check: no regression on a real GNOME damage-only stream (Firefox shows still frames after motion,\nso nightly is not stuck here either)', fontsize=11)
fig.tight_layout(); fig.savefig(D / '2-live-f44-gnome-firefox.png')
