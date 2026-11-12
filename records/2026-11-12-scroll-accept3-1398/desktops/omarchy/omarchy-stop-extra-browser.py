from pathlib import Path
import os,time,json,signal,subprocess
import pass2 as p
P=p.P;required=['firefox-end-0','firefox-end-1','firefox-top']
for n in required:
 r=json.loads((P/n/'result.json').read_text());assert r.get('pass'),(n,r)
deadline=time.monotonic()+150
while True:
 last=None
 for line in (P/'rpc.jsonl').read_text().splitlines():
  v=json.loads(line)
  if v['method']=='scroll.prepare' and v['reply'].get('ok'):last=v['reply']['result']['id']
 state=p.rpc('scroll.inspect',{'id':last}) if last else {'state':'done'}
 if state.get('state') in ['done','failed','cancelled']:break
 assert time.monotonic()<deadline,'current extra capture did not finish'
 time.sleep(.2)
owned=[]
for q in Path('/proc').iterdir():
 if not q.name.isdigit():continue
 try:
  a=(q/'cmdline').read_bytes().split(bytes([0]));isdriver=len(a)>1 and a[1]==str(P/'browsercases.py').encode();isff=str(P/'ffprofile').encode() in a and any(b'firefox' in x for x in a[:1])
  if isdriver or isff:owned.append({'pid':int(q.name),'kind':'extra-variant-driver' if isdriver else 'owned Firefox fixture'})
 except OSError:pass
for v in owned:
 try:os.kill(v['pid'],15)
 except ProcessLookupError:pass
(P/'extra-variant-scope-stop.json').write_text(json.dumps({'requiredBrowserRulerCases':required,'allRequiredPassed':True,'lastCaptureTerminalState':state.get('state'),'terminatedExactPids':owned,'reason':'Hyprland was not one of the five variant desktops in accept2. Stop unrequested extra variant loop after current capture ends; continue mandatory capfit/notice/MCP/export stages. Completed extras retained.'},indent=2));time.sleep(1)
subprocess.run(['python3',str(P/'variant-oracle.py')],check=False)
print('EXTRA_VARIANTS_STOPPED',owned,flush=True)
