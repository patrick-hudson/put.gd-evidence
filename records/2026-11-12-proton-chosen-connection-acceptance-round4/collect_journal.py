import pathlib,subprocess,sys,json
b=pathlib.Path('/tmp/p4a');script=(b/'export_sharing.py').read_text()
for h in sys.argv[1:]:
 r=subprocess.run(['python3',str(b/'remote.py'),h,"python3 - <<'PYREMOTE'\n"+script+'\nPYREMOTE'],capture_output=True,text=True,check=True)
 rows=json.loads(r.stdout);(b/'new'/h/'sharing-journal.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(h,'revoked',len({x['historyId'] for x in rows if x['action']=='revoke' and x['status']=='revoked'}),'unknown',sum(x['status']=='unknown' for x in rows))
