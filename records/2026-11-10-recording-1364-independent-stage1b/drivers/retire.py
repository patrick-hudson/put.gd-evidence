import pathlib,json,hashlib,sys,subprocess
base=pathlib.Path('/home/patrick/work/s1364b/src');run=base/'work/lab-runs'/sys.argv[1];evidence=pathlib.Path('/home/patrick/work/s1364b/evidence')/sys.argv[1];evidence.mkdir(parents=True,exist_ok=True)
s=json.loads((run/'state.json').read_text());(evidence/'state.json').write_text(json.dumps(s,indent=1)+'\n')
# Results and clips have already been copied from the guest into this evidence directory.
(run/'state.json').stat()
completion=dict(run=str(run),runId=s['id'],completed=True,outcome=sys.argv[2] if len(sys.argv)>2 else 'failed')
(evidence/'completion.json').write_text(json.dumps(completion,indent=1)+'\n')
files={str(p.relative_to(evidence)):hashlib.sha256(p.read_bytes()).hexdigest() for p in evidence.rglob('*') if p.is_file() and p.name!='manifest.json'}
manifest=dict(schemaVersion=1,kind='vm-overlay-cleanup-evidence',**completion,files=files)
(evidence/'manifest.json').write_text(json.dumps(manifest,indent=1)+'\n')
lab=[sys.executable,str(base/'tools/lab/lab.py')]
subprocess.run(lab+['reset','--run',str(run)],check=True)
cmd=lab+['cleanup','--run',str(run),'--images-root','/home/patrick/work/put.gd/work/lab-images','--evidence-manifest',str(evidence/'manifest.json')]
subprocess.run(cmd+['--dry-run'],check=True);subprocess.run(cmd,check=True)
