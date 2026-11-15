import accept as A,subprocess,json,time,shutil,sys
from pathlib import Path
P=A.P;L=A.L;d=P/(sys.argv[1] if len(sys.argv)>1 else 'control-audit-attempt1');d.mkdir(mode=0o700)
for n in ['mcp-results.json','control-audit.log','mcp-retry-process.json','mcp-retry-cleanup.json','retry-control-audit.log']:
 if (P/n).exists():shutil.move(P/n,d/n)
(d/'README.md').write_text('# Read-only query-size harness correction\n\nHistory supports pages of 1 to 200 records. The first audit and optional MCP History comparisons requested 1000 and received invalid_query. Capture prepare/toggle/stop/cancel operations themselves ran. The corrected audit uses limit 200 with offsets, and the MCP client now rejects every production error rather than ignoring optional comparison responses. This preserves the first attempt and reruns the MCP capture/control/cancel proof on its own real browser. The mixed native reference was already saved before the invalid list request.\n')
try:
 profile=P/'profile-firefox'
 if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
 L.browser_start('firefox');b,_=L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 q=subprocess.run([A.os.environ['SFA_MCP_PYTHON'],str(P/'mcptest.py')],capture_output=True,text=True);(P/'mcp-retry-process.json').write_text(json.dumps({'exit':q.returncode,'stdout':q.stdout,'stderr':q.stderr},indent=1))
 if q.returncode!=0:
  rows=json.loads((P/'mcp-results.json').read_text());ids=[]
  for row in rows:
   if row['tool']=='prepare_scroll_capture':
    data=json.loads(next(c['text'] for c in row['response']['content'] if c['type']=='text'));sid=data.get('result',{}).get('id')
    if sid:ids.append(sid)
  for sid in ids:
   try:
    if A.rpc('scroll.inspect',{'id':sid}).get('state') in ['ready','preparing','capturing','finishing','selecting']:A.rpc('scroll.cancel',{'id':sid})
   except Exception:pass
  raise RuntimeError('MCP retry failed; owned active preparations were canceled; stderr is retained')
finally:L.browser_stop()
# The mixed reference was saved by the exact same browser before its list failed.
v=next(x['value'] for x in json.loads((P/'extra-results.json').read_text()) if x['label']=='done-mixed')
records=A.rpc('history.list',{'limit':200})['records'];r=next(x for x in records if x['operationId']==v['id']);shutil.copyfile(r['local']['path'],P/'mixed-capture.png')
from PIL import Image
reference=Image.open(P/'mixed-reference.png');meta={'capture':v,'rect':[240,200,1440,820],'reference':{'docHeight':reference.height,'w':reference.width},'viewport':json.loads((P/'viewport.json').read_text()),'note':'Original native reference was written in the mixed capture browser before the optional History list failed. Capture admission recovered by exact operation ID with supported limit 200. Calibration matches the original extra-run log.'};(P/'mixed-comparison-info.json').write_text(json.dumps(meta,indent=1))
with (P/'control-audit.log').open('w') as f:subprocess.run(['python3',str(P/'audit-controls.py')],stdout=f,stderr=subprocess.STDOUT,check=True)
print('CONTROL AUDIT RETRY COMPLETE',flush=True)
