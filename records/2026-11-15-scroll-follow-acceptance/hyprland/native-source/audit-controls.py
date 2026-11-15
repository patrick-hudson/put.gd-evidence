import accept as A,json,hashlib,stat,os
P=A.P;extra=json.loads((P/'extra-results.json').read_text());mcp=json.loads((P/'mcp-results.json').read_text());ids={}
for row in extra:
 if row['label']=='agent-inspect':ids['cliCancel']=row['value']['id']
for row in mcp:
 a=row['arguments']
 if row['tool']=='control_scroll_capture' and a['command'] in ['cancel','stop']:ids['mcp'+a['command'].title()]=a['id']
assert set(ids)=={'cliCancel','mcpCancel','mcpStop'},ids
records=[];offset=0
while True:
 v=A.rpc('history.list',{'limit':200,'offset':offset});chunk=v['records'];records.extend(chunk);offset+=len(chunk)
 if not chunk or offset>=v['total']:break
result={'operationIds':ids,'totalHistoryRows':len(records),'matchingHistory':{},'stagingFiles':[str(x.relative_to(P/'d')) for x in (P/'d').rglob('*') if x.is_file() and '/scroll/' in str(x)]}
for label,sid in ids.items():
 matches=[x for x in records if x.get('operationId')==sid]
 result['matchingHistory'][label]=[{k:r.get(k) for k in ['id','operationId','uploadStatus','local','sha256']} for r in matches]
 if label.endswith('Cancel'):assert not matches,(label,matches)
 else:
  assert len(matches)==1 and matches[0]['uploadStatus']=='local_only';f=A.Path(matches[0]['local']['path']);s=f.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid();assert hashlib.sha256(f.read_bytes()).hexdigest()==matches[0]['sha256']
assert not result['stagingFiles'],result
(P/'control-history-staging-audit.json').write_text(json.dumps(result,indent=1));print(json.dumps(result,indent=1))
