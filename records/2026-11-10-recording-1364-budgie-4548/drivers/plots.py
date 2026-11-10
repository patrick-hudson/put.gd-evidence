import pathlib,json,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=pathlib.Path(sys.argv[1]);x=json.load(open(root/'comparison.json'));out=root/'plots';out.mkdir(exist_ok=True);plt.rcParams.update({'font.size':10,'svg.fonttype':'none'})
fig,axs=plt.subplots(2,1,figsize=(8.5,6.1),layout='constrained',gridspec_kw={'height_ratios':[1.3,1]})
ax=axs[0];ax.axhspan(-33,33,color='#dcecdc',alpha=.6);ax.axhline(0,color='#777777',lw=.7);ax.axhline(-45,color='#af3640',ls='--',lw=.8);ax.axhline(125,color='#af3640',ls='--',lw=.8)
labels=[]
for i,c in enumerate(x['cells']):
 v=c['medians'];color='#3976bb'if c['mode']=='still'else'#874ab2';ax.plot([i,i],[min(v),max(v)],color=color,lw=2,alpha=.65)
 for j,y in enumerate(v):ax.scatter(i+(j-1.5)*.065,y,s=30,color=color,zorder=4)
 ax.plot([i-.18,i+.18],[c['medianOfMedians']]*2,color='#222222',lw=2);labels.append(c['build']+' '+('parked'if c['mode']=='still'else'swept'))
ax.set(xticks=range(4),xticklabels=labels,ylabel='Audio minus picture (ms)',ylim=(-70,145),title='All highlights on; region; lead 3 s; four runs per cell');ax.grid(axis='y',alpha=.15)
ax=axs[1];ax.axhline(0,color='#777777',lw=.8)
for i,c in enumerate(x['contrasts']):
 v=c['pairedSweepMinusStill'];ax.plot([i,i],[min(v),max(v)],color='#777777',lw=2)
 for j,y in enumerate(v):ax.scatter(i+(j-1.5)*.05,y,s=30,color='#3976bb'if i==0 else'#b06e31',zorder=4)
 ax.plot([i-.16,i+.16],[c['medianPairedDifference']]*2,color='#222222',lw=2)
ax.set(xticks=[0,1],xticklabels=['4538 before','4548 after'],ylabel='Paired swept − parked (ms)',title='Within-build differences: ranges overlap',ylim=(-60,40));ax.grid(axis='y',alpha=.15)
fig.suptitle('Budgie before / after comparison',fontsize=13);fig.savefig(out/'comparison.svg');fig.savefig(out/'comparison.png',dpi=160);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(11,4),sharey=True,layout='constrained')
for ax,rs,title in [(axs[0],x['oldRows'],'4538 before'),(axs[1],x['newRows'],'4548 after')]:
 for r in rs:
  if r.get('pointer')not in('still','sweep'):continue
  mode=r['pointer'];ax.plot(r['pairTimesS'],r['offsetsMs'],marker='o',ms=2,lw=1,alpha=.7,color='#3976bb'if mode=='still'else'#874ab2',label=mode if r['repeat']==1 else None)
 ax.axhline(0,color='#777777',lw=.7);ax.set(title=title,xlabel='Clip time (s)',ylabel='Audio minus picture (ms)');ax.grid(alpha=.2);ax.legend()
fig.suptitle('Every marker pair: parked versus swept, four clips each');fig.savefig(out/'ordered-pairs.svg');fig.savefig(out/'ordered-pairs.png',dpi=150);plt.close(fig)
