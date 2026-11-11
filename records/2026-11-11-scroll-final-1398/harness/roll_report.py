from pathlib import Path
import json
B=Path('/home/patrick/work/rolling-capture-research/acceptance/final');R=B/'record'
# Exact requested matrix, 32 observations per desktop. Extra diagnostics stay outside these totals.
physical=[('Qt ruler, 2,400 px',[f'plain-{i:02}' for i in range(5)]),('Browser ruler',[f'firefox-{i:02}' for i in range(5)]),('Qt text, wide',[f'qtfull-{i:02}' for i in range(2)]),('Qt text, narrow',[f'qtnarrowfull-{i:02}' for i in range(2)]),('GTK 4 text, wide',[f'gtkfull-{i:02}' for i in range(2)]),('GTK 4 text, narrow',[f'gtknarrowfull-{i:02}' for i in range(2)]),('Qt ruler, 24,000 px; cap 40,000',['long-00']),('Applied cap 2,000; warning + loopback upload',['cap-warning']),('Immediate capture after cap',['postcap-warning']),('Three rapid captures',[f'race-{i:02}' for i in range(3)]),('Stop halfway',['stop-middle-final']),('Stop during scroll-to-top',['stop-top2']),('Cancel; no row or staging files',['cancel']),('Halfway start, from-top on',['half-on']),('Halfway start, from-top off',['half-off']),('Fractional scale',['scaled-00']),('Agent-only MCP; PNG fetched',['mcp']),('Safe shortcut + real drag',['user'])]
guest=[['native%02d'%i for i in range(1,6)],['rapid%02d'%i for i in range(1,6)],['qt1280-1','qt1280-2'],['qt600-1','qt600-2'],['gtk1280-1','gtk1280-2'],['gtk600-1','gtk600-2'],['long1'],['cap'],['postcap'],['burst%02d'%i for i in range(1,4)],['stop-mid'],['stop-top-1'],['cancel'],['half-on'],['half-off'],['fraction'],['mcp1'],['user']]
cols=['m74 Cinnamon X11','f44 GNOME Wayland','d69 Plasma 6.3.6','Omarchy Hyprland','Budgie labwc','neon KWin 6.8','Kubuntu KWin 6.6']
keys=['m74','f44','d69','o','b','n','k'];totals={};cells={};failures=[]
for key in keys:
 tally=dict(E=0,H=0,W=0,C=0,N=0);cs=[]
 for j,(label,names) in enumerate(physical):
  names=list(names) if key in keys[:3] else guest[j];counts=dict(E=0,H=0,W=0,C=0,N=0)
  for name in names:
   if key in keys[:3]:
    if key=='m74' and name=='scaled-00':name='scale150-clean'
    if key=='f44' and name=='cancel':name='cancel-correct'
    p=R/'physical'/key/'cases'/name/'result.json'
    if not p.exists():cat='N'
    else:
     a=json.loads(p.read_text());end=a.get('capture',{}).get('endReason');ok=a.get('pass',a.get('verification',{}).get('pass',False))
     cat='C' if j==12 and ok else 'H' if end in ['stopped','lost_track'] and ok else 'E' if ok else 'W'
   else:
    p=R/'guests'/(key+'fin')/'analysis.json'
    a=json.loads(p.read_text()).get(name,{}) if p.exists() else {};v=a.get('verify') or {};end=a.get('end')
    cat='N' if not a else 'C' if j==12 and a.get('state')=='cancelled' else 'H' if end in ['stopped','lost_track'] and (v.get('ok') or v.get('exactPrefix')) else 'E' if v.get('ok') else 'W'
   counts[cat]+=1;tally[cat]+=1
   if cat in ['W','N']:failures.append((key,label,name,cat))
  cs.append(' / '.join(f'{n} {c}' for c,n in counts.items() if n))
 totals[key]=tally;cells[key]=cs
lines=['| Case | '+' | '.join(cols)+' |','|---|'+'---|'*7]
for i,(label,_) in enumerate(physical):lines.append('| '+label+' | '+' | '.join(cells[k][i] for k in keys)+' |')
lines.append('| **Totals** | '+' | '.join(' / '.join(f'{n} {c}' for c,n in totals[k].items() if n) for k in keys)+' |')
(B/'table.md').write_text('\n'.join(lines)+'\n');(B/'totals.json').write_text(json.dumps({'desktops':totals,'overall':{c:sum(v[c] for v in totals.values()) for c in ['E','H','W','C','N']},'nonpass':failures},indent=2));print(json.dumps(totals))
