import json,pathlib,sys,statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=pathlib.Path(sys.argv[1]);out=root/'plots';out.mkdir(exist_ok=True)
a=json.load(open(root/'analysis.json'));rows=a['runs'];cells={c['name']:c for c in a['cells']}
plt.rcParams.update({'font.size':10,'svg.fonttype':'none'})
fig=plt.figure(figsize=(9.2,6.4),layout='constrained');grid=fig.add_gridspec(2,2);axes=[fig.add_subplot(grid[0,0]),fig.add_subplot(grid[0,1]),fig.add_subplot(grid[1,:])]
allv=[v for c in cells.values()for v in c['values']];limits=(min(-70,min(allv)-20),max(145,max(allv)+20))
groups=[('Region',[f'region {lead}s {on}'for lead in(3,6)for on in('on','off')],['On / 3 s','Off / 3 s','On / 6 s','Off / 6 s']),('Monitor',[f'monitor {lead}s {on}'for lead in(3,6)for on in('on','off')],['On / 3 s','Off / 3 s','On / 6 s','Off / 6 s']),('Pointer experiment: region, lead 3 s',['pointer still on','pointer sweep on','pointer sweep off'],['Parked, on','Sweep, on','Sweep, off'])]
for ax,(title,names,labels)in zip(axes,groups):
 ax.axhspan(-33,33,color='#dcecdc',alpha=.6);ax.axhline(0,color='#777777',lw=.7);ax.axhline(-45,color='#af3640',ls='--',lw=.8);ax.axhline(125,color='#af3640',ls='--',lw=.8)
 for x,name in enumerate(names):
  c=cells[name];color='#3976bb'if name.endswith('on')else'#b06e31'
  if 'sweep on'in name:color='#874ab2'
  ax.plot([x,x],[c['min'],c['max']],color=color,lw=2,alpha=.7)
  for j,y in enumerate(c['values']):ax.scatter(x+(j-1.5)*.065,y,s=30,color=color,zorder=4)
  ax.plot([x-.18,x+.18],[c['median'],c['median']],color='#222222',lw=2)
 ax.set(title=title,xticks=range(len(labels)),xticklabels=labels,ylim=limits,ylabel='Audio minus picture (ms)');ax.grid(axis='y',alpha=.15);ax.spines[['top','right']].set_visible(False)
fig.suptitle('Budgie / AppImage 4538 — four runs per cell',fontsize=13)
fig.savefig(out/'cell-medians.svg');fig.savefig(out/'cell-medians.png',dpi=160);plt.close(fig)
fig,axs=plt.subplots(2,2,figsize=(11,7),sharey=True,layout='constrained')
for ax,(target,lead)in zip(axs.flat,[(t,l)for t in('region','monitor')for l in(3,6)]):
 for r in rows:
  if r.get('target')!=target or r['lead']!=lead or r['repeat']==0:continue
  on=r['highlights']=='on';ax.plot(r['pairTimesS'],r['offsetsMs'],marker='o',ms=2,lw=1,alpha=.65,color='#3976bb'if on else'#b06e31',label=r['highlights']if r['repeat']==1 else None)
 ax.axhline(0,color='#777777',lw=.7);ax.set(title=f'{target}, lead {lead} s',xlabel='Clip time (s)',ylabel='Audio minus picture (ms)');ax.grid(alpha=.2);ax.legend()
fig.suptitle('Every marker pair, in order; four clips per setting');fig.savefig(out/'ordered-pairs.svg');fig.savefig(out/'ordered-pairs.png',dpi=150);plt.close(fig)
fig,axs=plt.subplots(1,3,figsize=(12,4),sharey=True,layout='constrained')
for ax,(mode,on)in zip(axs,[('still','on'),('sweep','on'),('sweep','off')]):
 for r in rows:
  if r.get('pointer')==mode and r['highlights']==on:ax.plot(r['pairTimesS'],r['offsetsMs'],marker='o',ms=2,label='run '+str(r['repeat']))
 ax.axhline(0,color='#777777',lw=.7);ax.set(title=f'{mode}, highlights {on}',xlabel='Clip time (s)',ylabel='Audio minus picture (ms)');ax.grid(alpha=.2);ax.legend(fontsize=8)
fig.suptitle('Pointer experiment: every marker pair, lead 3 s');fig.savefig(out/'pointer-pairs.svg');fig.savefig(out/'pointer-pairs.png',dpi=150);plt.close(fig)
