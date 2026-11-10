import sys,pathlib,hashlib,json,subprocess
sys.path.insert(0,'/tmp/b1364');from control import G
E=pathlib.Path('/home/patrick/work/putgd-evidence/2026-11-10-recording-1364-budgie-final-visible');mapping={}
for part,source in [('runs','r')]:
 for p in (E/part).rglob('*'):
  if p.is_file():
   rel=p.relative_to(E).as_posix();s=source+'/'+p.relative_to(E/part).as_posix()
   if '/captures/' in s:s=s.replace('/captures/','/archive/images/')
   mapping[rel]=s
for name in ('visible.json','audio.json','build-version.txt','socket-preflight.json','default-sink.txt','default-source.txt','sources-before.txt','labwc-version.txt','budgie-version.txt'):mapping[name]=name
script="import sys,pathlib,json,hashlib; m=json.load(sys.stdin); root=pathlib.Path('/home/lab/b1364v');print(json.dumps({k:hashlib.sha256((root/v).read_bytes()).hexdigest() for k,v in m.items()}))"
r=subprocess.run(G+['python3 -c '+__import__('shlex').quote(script)],input=json.dumps(mapping),capture_output=True,text=True,check=True)
remote=json.loads(r.stdout);bad=[]
for k,v in remote.items():
 if hashlib.sha256((E/k).read_bytes()).hexdigest()!=v:bad.append(k)
out={'verifiedFiles':len(remote),'mismatches':bad,'sha256':remote};(E/'identity/export-verification.json').write_text(json.dumps(out,indent=2)+'\n');print({'files':len(remote),'mismatches':bad});assert not bad
