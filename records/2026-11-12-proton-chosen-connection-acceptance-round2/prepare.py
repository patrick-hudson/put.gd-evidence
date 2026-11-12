from pathlib import Path
import json,re
b=Path('/tmp/pr1414r2'); p=b/'d69/pr';d=json.loads((p/'results.json').read_text())
first=[]
for name,sec in [('file-64k',3.9),('file-1m',5.53)]: first.append({'name':name,'passed':True,'state':'completed','seconds':sec,'note':'PASS and total preserved in interrupted run.log; detailed CLI record lost'})
first.append({'name':'file-8m','passed':False,'state':'completed','note':'App log completion only; CLI timing and harness verdict lost to adapter interruption','seconds':8.152,'timingSource':'app Operation accepted to Operation finished, not CLI invocation'})
original=[x for x in d['results'] if not x['name'].startswith('sequential') and x['name']!='revoke-additions']
original.insert(-1,{'name':'link-answers','passed':False,'state':'not_run','note':'not reached before instrumentation error; links revoked in continuation'})
d['results']=first+original+[x for x in d['results'] if x['name'].startswith('sequential') or x['name']=='revoke-additions'];(p/'combined-results.json').write_text(json.dumps(d,indent=1))
p=b/'report.py';s=p.read_text().replace("f=B/h/'pr/results.json'","f=B/h/('pr/combined-results.json' if h=='d69' else 'pr/results.json')")
s=s.replace("if i.get('error'):return i['error']", "if i.get('timingSource'):return str(i['seconds'])+'†'\n if i.get('error'):return i['error']\n if i.get('state')=='not_run':return 'not run'")
s=s.replace("for f in ['results.json','summary.txt','capture-checks.json','display-state.json','black-immediate-repeat.json','nightly-control-exit.json']:","for f in ['results.json','combined-results.json','interrupted-results.json','summary.txt','capture-checks.json','display-state.json','black-immediate-repeat.json','nightly-control-exit.json','revocation-verification.json','observed-operations.jsonl']:")
s=s.replace("for f in ['round2.py','drive.py','ci.json','nightly.json','merge-provenance.json']:","for f in ['round2.py','round2-first-attempt.py','drive.py','drive-first-attempt.py','resume.py','ci.json','nightly.json','merge-provenance.json','package-sha256.txt']:")
p.write_text(s)
