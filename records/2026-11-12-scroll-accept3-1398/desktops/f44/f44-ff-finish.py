from pathlib import Path
import subprocess,os,time,json
P=Path('/home/patrick/work/s3a')
while not (P/'accept3-campaign.done').exists():time.sleep(2)
# The Chromium retry completes first; repair the skipped Firefox profile separately.
for site in ['pr','wiki','py','mdn','repo','hn','rust']:
 for mode in ['half','top']:
  d=P/'runs'/('accept3-ff-'+site+'-'+mode)
  if d.exists() and not (d/'result.json').exists():d.rename(d.with_name(d.name+'-harness-attempt2'))
with (P/'firefox-retry.console').open('w') as log:r=subprocess.run(['python3',str(P/'live-accept3-v2.py'),'campaign','accept3','firefox','pr,wiki,py,mdn,repo,hn,rust','half,top'],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,SF7=str(P),SF7_VNC='5901',SF7_NOVERIFY='1',ACCEPT3_MAX_HEIGHT='60000'))
print('FIREFOX_RETRY_EXIT',r.returncode,flush=True)
results=list((P/'runs').glob('accept3-*/result.json'));names={f.parent.name for f in results};expected={'accept3-'+b+'-'+s+'-'+m for b in ['ff','cr'] for s in ['pr','wiki','py','mdn','repo','hn','rust'] for m in ['half','top']};(P/'live-completeness.json').write_text(json.dumps({'expected':len(expected),'present':len(names&expected),'missing':sorted(expected-names)},indent=2))
# Finished desktop work is restored immediately; comparisons run later over SSH.
r=subprocess.run(['python3',str(P/'f44-restore.py')]);print('RESTORE_EXIT',r.returncode,flush=True)
if r.returncode==0:(P/'physical-restored.done').write_text('done')
