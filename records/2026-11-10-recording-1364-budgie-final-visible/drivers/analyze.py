import pathlib,json,hashlib,re,statistics
E=pathlib.Path('/home/patrick/work/putgd-evidence/2026-11-10-recording-1364-budgie-final-visible')
m=json.loads((E/'visible.json').read_text());d=json.loads((E/'diagnostics.json').read_text());rows=[];audits=[]
for r in m['order']:
 a=E/'runs'/r['tag']/'method-audit.jsonl'
 calls=[json.loads(s) for s in a.read_text().splitlines()];audits+=calls
 r['diagnostics']=d[r['tag']];r['withinAcceptanceBound']=-45<=r['medianMs']<=125;r['withinOneFrameTarget']=abs(r['medianMs'])<=33
 r['overlayCallCount']=sum(x.get('method')=='recording.overlay' for x in calls)
 rows.append(r)
assert len(rows)==8 and all(x['overlayCallCount']==0 for x in rows)
assert all(r['exitCode']==0 and not r.get('error') and not r.get('problems') for r in rows)
m['order']=rows;m['overlayCallCount']=0;m['allWithinBound']=all(r['withinAcceptanceBound']for r in rows);m['earlierThanMinus45']=[r['tag']for r in rows if r['medianMs']< -45]
m['protocol']='region 0,0,1280,400; lead3s; control bar visible throughout; no recording.overlay; on/off repeated4; same marker and private system sink; mic off'
m['driverSha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (E/'drivers').glob('*')if p.is_file()}
(E/'summary.json').write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps({'rows':[(r['tag'],r['medianMs'],r['diagnostics']['frameAge'],r['withinOneFrameTarget'])for r in rows],'allWithinBound':m['allWithinBound'],'loadStart':m['loadAtStart'],'loadEnd':m['loadAtEnd'],'audioRemoved':m['audioRemoved']},indent=2))
