from pathlib import Path
import sys,json,shlex,subprocess
B=Path('/home/patrick/work/svm1398');D=Path('/home/patrick/work/scn');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
k=sys.argv[1];r=B/'repo/work/lab-runs'/(k+'cn');o=D/'ev'/(k+'cn');assert (o/'campaign.done').exists()
code='''from pathlib import Path
import json,hashlib,struct
p=Path('/tmp/v3');got=[]
for f in (p/'received').glob('*'):
 if not f.is_file():continue
 b=f.read_bytes();i=b.find(b'\\x89PNG\\r\\n\\x1a\\n')
 if i<0:continue
 j=i+8
 while j+12<=len(b):
  n=struct.unpack('>I',b[j:j+4])[0];kind=b[j+4:j+8];j+=12+n
  if kind==b'IEND':got.append(hashlib.sha256(b[i:j]).hexdigest());break
out={}
for name in ['cap','postcap','mcp']:
 f=p/'cases'/name/'capture.png'
 if f.exists():
  sha=hashlib.sha256(f.read_bytes()).hexdigest();out[name]={'sha256':sha,'loopbackReceived':sha in got}
(p/'upload-verification.json').write_text(json.dumps({'receivedPngCount':len(got),'cases':out},indent=2))
print(out)
'''
print(lab.guest_session(r,'python3 -c '+shlex.quote(code)))
lab.get(r,'/tmp/v3/upload-verification.json',o/'upload-verification.json')
s=json.loads((r/'state.json').read_text());(o/'run-identity.json').write_text(json.dumps({key:s[key] for key in ['id','profile','golden','golden_sha256','pid','ssh_port','vnc_display'] if key in s},indent=2))
