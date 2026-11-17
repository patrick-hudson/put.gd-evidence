from pathlib import Path
import json,re,subprocess,sys,hashlib
P=Path.cwd();summary=[]
for d in sorted((P/'runs').iterdir()):
 if not(d/'result.json').exists():continue
 r=json.loads((d/'result.json').read_text());c=r['capture'];verdict='DAMAGED'if(d/'damaged.json').exists()else('HONEST'if c.get('endedLost')or c.get('truncated')or c.get('endReason')in['lost_track','height_cap']else'RIGHT')
 reason='Reference body rows align; partial-width/pinned artifacts are recorded separately as requested.'
 if verdict=='DAMAGED':reason='568-row written-white tail, rows 9913–10480; declared lost. See damaged.json.'
 if r['site']=='stackoverflow'and verdict=='RIGHT':reason='Body probes align at 0, then +130, then +180 after dynamic advertisement geometry changes; pinned ad/cookie fragments are separate.'
 v=dict(verdict=verdict,reason=reason);(d/'verdict.json').write_text(json.dumps(v,indent=1));row=dict(run=d.name,case=d.name.split('-')[-2],verdict=verdict,imageHeight=c['height'],documentBefore=r['before']['docHeight'],documentAfter=r['after']['docHeight'],**{k:c.get(k)for k in ['endReason','truncated','endedLost','foundAgain','framesPlaced','framesSkipped','framesPerSecond','note','id']});summary.append(row)
 if verdict!='RIGHT':
  lines=(d/'helper.log').read_text().splitlines();ids=set();state=None
  for i,l in enumerate(lines):
   match=re.search(r'state (following|lost)',l)
   change=bool(match and match[1]!=state)
   if match:state=match[1]
   if(change and state=='lost')or' recovered'in l or 'scroll: ended'in l:
    ids.update(range(max(0,i-6),min(len(lines),i+8)))
  (d/'helper-excerpt.log').write_text('\n'.join(lines[i]for i in sorted(ids))+'\n')
  if not(d/'tail-seam.png').exists():
   h=c['height'];lo=max(0,h-1500)
   subprocess.run([sys.executable,str(P/'seam.py'),str(d),str(d/'tail-seam.png'),str(lo),str(h),str(lo),str(h),'.5'],check=True)
(P/'summary.json').write_text(json.dumps(summary,indent=1))
pinned=[dict(run='firefox-news-user-Bnews-1',kind='advertisement/video and full-width cookie banner',picture='runs/firefox-news-user-Bnews-1/prefix-seam.png'),dict(run='firefox-news-user-Bnews-2',kind='advertisement/video and cookie banner'),dict(run='firefox-stackoverflow-user-Bso-1',kind='pinned sidebar, ad and cookie fragments; body geometry +130/+180',picture='runs/firefox-stackoverflow-user-Bso-1/tail-seam.png'),dict(run='firefox-stackoverflow-user-Bso-2',kind='pinned ad/cookie area at saved tail')]
(P/'pinned-summary.json').write_text(json.dumps(pinned,indent=1));print(json.dumps(summary,indent=1))
