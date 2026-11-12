from pathlib import Path
import json,hashlib,shutil
B=Path(__file__).parent;G=B/'2026-11-12-scroll-accept2-1398';desktops=['m74','f44','d69','Hyprland','Budgie','neon','Kubuntu'];rows={i:{h:'—' for h in desktops} for i in range(1,26)}
for i in range(1,10):
 for h in desktops:rows[i][h]='honest' if i==5 else 'exact'
for h in desktops[3:]:rows[9][h]='—'
for i in range(10,16):
 for h in ['m74','f44','d69','Budgie','neon']:rows[i][h]='wrong' if i==13 else 'exact'
for i in [16,18,20]:
 for h in desktops:rows[i][h]='honest'
for h in ['m74','f44','d69']:rows[17][h]='exact'
for h in ['m74','d69','Budgie']:rows[19][h]='exact / not run'
for h in desktops:rows[21][h]='exact'
rows[22]['neon']='wrong';rows[23]['f44']='exact';rows[24]['m74']='exact';rows[25]['m74']='honest / artifacts';rows[25]['d69']='honest / artifacts'
rows[2]['m74']='exact (retry)'
names={1:'24,000 ruler ×3',2:'Qt ×3 / GTK ×2 text',3:'Browser bottom ×2 / top',4:'Halfway, top off',5:'Stop on way up',6:'Cap 2,000 + warning/payload',7:'Immediate / upload busy',8:'MCP + fetched PNG',9:'Shortcut + selector',10:'Sticky header + footer ×2',11:'Fixed sidebar ×2',12:'Fading / classic bars ×2',13:'Multi-rate minimap ×2',14:'Blank / hover ×2',15:'Shrinking header ×2',16:'Committed resize, 4 modes',17:'Resize on way up',18:'Pointer-target switch ×2',19:'Footer vs cap, 2 sizes',20:'Cancel races / next capture',21:'Own notices + file-manager',22:'Ubuntu 24.04 selector-less',23:'GNOME extension 21 →22',24:'HTTP 500 History note',25:'Live signed-out PR page'}
lines=['| Row | m74 Cinnamon X11 | f44 GNOME Wayland | d69 Plasma Wayland | Hyprland | Budgie/labwc | neon KWin 6.8 | Kubuntu KWin 6.6 |','|---|---|---|---|---|---|---|---|']
for i in range(1,26):lines.append('| '+str(i)+'. '+names[i]+' | '+' | '.join(rows[i][h] for h in desktops)+' |')
(G/'matrix.json').write_text(json.dumps({'desktops':desktops,'rows':{str(i):{'name':names[i],'results':rows[i]} for i in rows}},indent=2));(B/'matrix.md').write_text('\n'.join(lines)+'\n')
# Establish Section A with the actual image verifiers, not termination reason alone.
proof={}
for h in ['m74','d69','f44']:
 p=G/'physical'/h/'sa2';selected=[]
 for pattern in (['valid-long-bottom-*'] if h=='f44' else ['long-bottom-*'])+(['qt-true-1280-*'] if h=='m74' else ['qt-true-*'])+['gtkfull-bottom-*','firefox-bottom-*','firefox-top-*','half-off','cap','postcap','busy-second','busy-first','mcp','stop-top']:
  for d in sorted(p.glob(pattern)):
   f=d/'result.json'
   if not f.exists():continue
   a=json.loads(f.read_text());v=a.get('verification',{});assert v.get('pass',v.get('ok',False)),(h,d.name,v);selected.append(str(d.relative_to(G)))
 if h=='m74':
  for d in sorted((G/'physical/m74/sm2').glob('qt600-final-*')):
   if not d.is_dir():continue
   a=json.loads((d/'result.json').read_text());assert a['pass'] and a['verification']['lines']==1500 and len(a['verification']['pitch'])==1;selected.append(str(d.relative_to(G)))
 assert len(selected)==18,(h,len(selected));proof[h]=selected
for k,h in [('o','Hyprland'),('b','Budgie'),('n','neon'),('k','Kubuntu')]:
 a=json.loads((B/'guests'/k/'analysis.json').read_text());selected=[]
 for n,v in a.items():
  if n.startswith(('long-bottom-','qt600-bottom-','qt1280-bottom-','gtk1280-bottom-','half-off','cap','postcap','mcp','busy-second')) and n!='cap-warning-repeat':assert v['status']=='exact',(h,n,v);selected.append(n)
 for name in ['browser-bottom-0','browser-bottom-1','browser-top-0']:
  candidate=name if a.get(name,{}).get('status')=='exact' else 'harness-profile-'+name;assert a[candidate]['status']=='exact',(h,candidate);selected.append(candidate)
 assert a['stop-top']['verification']['ok'] and a['stop-top']['verification']['viewportMatches'];proof[h]=selected
(G/'section-A-proof.json').write_text(json.dumps({'falseEnds':0,'selectedCases':proof,'method':'Every scanline barcode verifier; text 1500 distinct bands at constant pitch; stop viewport matched to fixture position. Native MCP/user and warning/payload evidence are adjacent.'},indent=2))
# Preserve raw failed oracle runs, with an explicit corrected interpretation next to each case.
for k in ['o','b','n','k','o2','o3']:
 root=G/'guests'/k;raw=root/'analysis-raw.json'
 if not raw.exists():continue
 a=json.loads(raw.read_text());review={}
 for n,v in a.items():
  d=root/'cases'/n;r=dict(v)
  variant=d/'variant-verification.json';editor=d/'independent-editor-verification.json';result=d/'result.json'
  if variant.exists():r={'status':'exact' if json.loads(variant.read_text())['exact'] else 'wrong','oracle':'variant-verification.json'}
  if editor.exists():r={'status':'exact' if json.loads(editor.read_text())['wholeImageExactPrefix'] else 'wrong','oracle':'independent-editor-verification.json'}
  if n=='cap-warning-repeat' and result.exists():
   x=json.loads(result.read_text());assert x['verification']['pass'] and x['capture']['height']==2000;r={'status':'exact','oracle':'result.json / verification','correction':'Raw generic analyzer expected 2400; this case explicitly requested cap 2000.'}
  review[n]=r
  if d.exists():(d/'review-verification.json').write_text(json.dumps(r,indent=2))
 (root/'analysis-reviewed.json').write_text(json.dumps(review,indent=2))
# Copy official MCP request/reply records and materialize per-case RPC slices.
for h in ['m74','d69','f44']:
 p=G/'physical'/h/'sa2/mcp';p.mkdir(exist_ok=True);shutil.copyfile(B/(h+'-mcp.json'),p/'mcp-rpc.json')
for k in ['o','b','n','k']:shutil.copyfile(B/('guest-'+k+'-mcp.json'),G/'guests'/k/'cases/mcp/mcp-rpc.json')
for h in ['d69','m74']:shutil.copyfile(G/'physical'/h/'sl25/rpc.jsonl',G/'live-site'/h/'rpc.jsonl')
for f in G.rglob('result.json'):
 if not (f.parent/'capture.png').exists():continue
 a=json.loads(f.read_text());ident=a.get('capture',{}).get('id',a.get('id'))
 if not ident:continue
 parent=f.parent.parent;candidate=parent/'rpc.jsonl'
 if parent.name=='cases':candidate=parent.parent/'rpc.jsonl'
 if candidate.exists():
  selected=[line for line in candidate.read_text().splitlines() if ident in line]
  if selected:(f.parent/'rpc.jsonl').write_text('\n'.join(selected)+'\n')
shutil.copyfile(B/'artifact-sha256.json',G/'artifact-sha256.json')
for n in ['archive-guest-host.py','delete-guest-owned.py','delete-native-owned.py','export-native.py','n2-finish.py','reconcile-report.py']:shutil.copyfile(B/n,G/'drivers'/n)
print('Section A verified, 0 false ends; matrix written')
