import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json,pathlib
root=pathlib.Path(__file__).resolve().parent;rows=json.load(open(root/'summary.json'));labels=['Monitor\nstill','Monitor\nsweep','Region\nstill','Region\nsweep','Off\nsweep','Same\nsession']
fig,axes=plt.subplots(2,1,figsize=(11,7.2),layout='constrained')
ax=axes[0];ax.axhspan(-45,125,color='#d8efe3',alpha=.7,label='Acceptance −45…+125 ms');ax.axhspan(-33.3,33.3,color='#c1d8ee',alpha=.8,label='One-frame target ±33.3 ms');ax.axhline(0,color='#555',lw=.8);ax.axhline(-45,color='#39805b',ls='--',lw=.8);ax.axhline(125,color='#39805b',ls='--',lw=.8)
for i,r in enumerate(rows):
 v=r['audioMedianMs'];ax.scatter(i,v,s=65,color='#c86a18' if abs(v)>33.3 else '#204c7c',zorder=3);ax.annotate(f'{v:+g}',(i,v),xytext=(0,10),textcoords='offset points',ha='center',fontsize=10)
ax.set(xticks=range(6),xticklabels=labels,ylim=(-58,138),ylabel='Audio minus picture (ms)',title='Exported audio median — one clip per condition');ax.grid(axis='y',alpha=.2);ax.legend(loc='upper right',fontsize=8)
ax=axes[1];ax.axhline(0,color='#555',lw=.8);ax.axhline(-70,color='#b13c3c',ls='--',label='Early bound −70 ms; upper bound +250 ms')
for k,color in enumerate(['#2474a9','#298b68','#9960a5']):
 xs=[];ys=[]
 for i,r in enumerate(rows):
  c=r['ring']['checks'][k]
  if c['seen']:xs.append(i+(k-1)*.08);ys.append(c['ringMinusEffectMs'])
 ax.scatter(xs,ys,color=color,s=36,label=f'Click {k+1}',zorder=3)
ax.scatter([2.08],[-100],marker='*',s=180,color='#c52929',zorder=4);ax.annotate('−100 ms: timing gate fails',(2.08,-100),xytext=(2.6,-108),arrowprops=dict(arrowstyle='->',color='#b13c3c'),color='#a02020',fontsize=9);ax.text(4,9,'0/3 rings',ha='center',fontsize=9)
ax.set(xticks=range(6),xticklabels=labels,ylim=(-120,25),ylabel='Ring minus visible client effect (ms)',title='Click timing measured inside the retained clip');ax.grid(axis='y',alpha=.2);ax.legend(loc='lower left',fontsize=8,ncol=2)
fig.suptitle('Hyprland / Omarchy — put.gd build 4548 · k72 KVM guest, 2 vCPU',fontsize=13)
fig.savefig(root/'alignment-and-clicks.png',dpi=160)
