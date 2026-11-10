import pathlib,json
root=pathlib.Path.home()/'cursor-probe';rid=json.load(open(root/'inspect.json'))['recordingId'];alllines=[]
for p in (root/'state').rglob('*.jsonl'):alllines.extend(json.loads(l) for l in p.read_text().splitlines())
started=next(x for x in alllines if x.get('message')=='Helper started' and x.get('operationId')==rid);pid=started['fields']['pid']
lines=[x for x in alllines if x.get('pid')==pid and 'ext_image_copy_capture_cursor_session_v1' in x.get('message','')]
out=dict(recordingId=rid,helperPid=pid,started=started,lines=lines)
assert any('create_pointer_cursor_session' in x['message'] for x in lines)
assert any('get_capture_session' in x['message'] for x in lines)
assert any('.enter()' in x['message'] for x in lines)
(root/'cursor-witness.json').write_text(json.dumps(out,indent=1));print('confirmed actual recording helper',pid,'cursor session; witness lines',len(lines))
