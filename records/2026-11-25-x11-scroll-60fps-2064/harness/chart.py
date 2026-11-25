import json, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
d = json.load(open(sys.argv[1])); out = sys.argv[2]
runs = [r for r in d if 'name' in r]
def build(n): return 'cand' if 'cand1' in n else 'nightly'
def pace(n): return 'brisk' if ('brisk' in n or '-b' in n.split('user-')[-1]) else 'normal'
agg = {}
for r in runs:
    n = r['name']
    if 'user' not in n: continue
    k = (build(n), pace(n)); a = agg.setdefault(k, [0, 0, 0])
    a[0] += 1; a[1] += r['capture']['foundAgain'] or 0; a[2] += 1 if (r['capture']['foundAgain'] or 0) else 0
INK, MUTED, N, C, ACC = '#1f2328', '#656d76', '#9aa4ae', '#c8961e', '#cf222e'
fig, axes = plt.subplots(1, 3, figsize=(15, 5.2), gridspec_kw={'width_ratios': [1.3, 1, 1.2]})
fig.patch.set_facecolor('white')
# 1 losses
ax = axes[0]
xs = [0, 1]
for i, p in enumerate(['normal', 'brisk']):
    nv = agg[('nightly', p)][1]; cv = agg[('cand', p)][1]
    ax.bar(i - 0.18, nv, 0.34, color=N, label='nightly 26.1125.7045 (30/s)' if i == 0 else None)
    ax.bar(i + 0.18, cv, 0.34, color=C, label='this PR (60/s)' if i == 0 else None)
    ax.text(i - 0.18, nv + 0.3, f'{nv}', ha='center', color=INK, fontsize=12)
    ax.text(i + 0.18, cv + 0.3, f'{cv}', ha='center', color=INK, fontsize=12, fontweight='bold')
ax.set_xticks(xs, [f"normal pace\n({agg[('nightly','normal')][0]} runs each)", f"brisk pace\n({agg[('nightly','brisk')][0]} runs each)"])
ax.set_title('You scroll: times the page was lost\n(m74 Cinnamon X11, Firefox 158)', color=INK, fontsize=12, loc='left')
ax.legend(frameon=False, fontsize=10, loc='upper left')
ax.annotate('19 → 8', xy=(1.18, agg[('cand','brisk')][1]), xytext=(0.55, 16), color=ACC, fontsize=13, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=ACC))
ax.set_ylim(0, 22)
# 2 auto-scroll github
ax = axes[1]
g = {build(r['name']): r for r in runs if r['name'].startswith('firefox-github-auto')}
labels = ['nightly', 'this PR']
sk = [g['nightly']['capture']['framesSkipped'], g['cand']['capture']['framesSkipped']]
ax.bar([0, 1], sk, 0.5, color=[N, C])
ax.text(0, sk[0] + 6, f"{sk[0]} skipped\nhanded back\n(\"done\")", ha='center', color=INK, fontsize=10)
ax.text(1, sk[1] + 6, "0 skipped\nend_of_content", ha='center', color=ACC, fontsize=11, fontweight='bold')
ax.set_xticks([0, 1], labels); ax.set_ylim(0, 340)
ax.set_title('Auto-scroll, GitHub PR #1398\nframes skipped', color=INK, fontsize=12, loc='left')
# 3 cost
ax = axes[2]
x4 = {r['tag']: r for r in d if 'tag' in r}
def m(r): return r['meter']['helperCpuPct']
userc = [r['meter']['helperCpuPct'] for r in runs if r['meter'] and build(r['name']) == 'cand' and '-b' in r['name']]
usern = [r['meter']['helperCpuPct'] for r in runs if r['meter'] and build(r['name']) == 'nightly' and '-b' in r['name']]
cats = ['m74, brisk you-scroll\n1920×922 (3 runs)', 'Xvfb\n1920×1080', 'Xvfb\n3840×2160']
nv = [sum(usern) / len(usern), m(x4['n-1080']), m(x4['n-4k'])]
cv = [sum(userc) / len(userc), m(x4['c-1080']), m(x4['c-4k'])]
for i in range(3):
    ax.bar(i - 0.18, nv[i], 0.34, color=N); ax.bar(i + 0.18, cv[i], 0.34, color=C)
    ax.text(i - 0.18, nv[i] + 2, f'{nv[i]:.0f}%', ha='center', fontsize=10, color=INK)
    ax.text(i + 0.18, cv[i] + 2, f'{cv[i]:.0f}%', ha='center', fontsize=10, color=INK, fontweight='bold')
ax.set_xticks(range(3), cats); ax.set_ylim(0, 135)
ax.set_title('Helper CPU (100% = one core)', color=INK, fontsize=12, loc='left')
ax.annotate('fell back to 30/s\nafter 2 s: same cost', xy=(2.18, cv[2]), xytext=(0.9, 118), color=ACC, fontsize=10, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=ACC))
for a in axes:
    for s in ('top', 'right'): a.spines[s].set_visible(False)
    a.tick_params(colors=MUTED)
fig.suptitle('X11 scrolling capture at 60 frames a second (#2064): CI candidate d526c747 vs published nightly', color=INK, fontsize=13, x=0.01, ha='left')
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(out, dpi=110)
print(agg)
