import pathlib,subprocess,time,json
root=pathlib.Path(__file__).parent;p=root/'last-poll-epoch.txt';now=time.time()
if p.exists() and now-float(p.read_text())<60:print('CI check deferred until one minute has elapsed');raise SystemExit()
p.write_text(str(now));r=subprocess.run(['gh','run','view','42784508070','-R','patrick-hudson/put.gd-desktop','--json','status,conclusion,headSha'],capture_output=True,text=True)
(root/'ci-poll.json').write_text(r.stdout)
with (root/'ci-polls.jsonl').open('a')as f:f.write(json.dumps({'epoch':now,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})+'\n')
print(r.stdout or r.stderr)
