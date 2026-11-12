from pathlib import Path
import subprocess,os,time,json,signal
P=Path('/home/patrick/work/s3a')
while not (P/'accept3-campaign.done').exists():time.sleep(2)
with (P/'missing-fixtures.console').open('w') as log:
 r=subprocess.run(['python3',str(P/'d69-corrected-missing.py')],stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0,'missing fixture suite crashed'
expected={'accept3-'+b+'-'+s+'-'+m for b in ['ff','cr'] for s in ['pr','wiki','py','mdn','repo','hn','rust'] for m in ['half','top']};present={f.parent.name for f in (P/'runs').glob('*/result.json')};(P/'live-completeness.json').write_text(json.dumps({'expected':28,'present':len(expected&present),'missing':sorted(expected-present)},indent=2))
r=subprocess.run(['python3',str(P/'d69-hotkey-restore.py')]);assert r.returncode==0,'hotkey restoration needs review before quitting'
import pass2 as p
p.rpc('ui.quit');time.sleep(3);owned=[]
for q in Path('/proc').iterdir():
 if not q.name.isdigit() or int(q.name)==os.getpid():continue
 try:
  if any(x.startswith(('XDG_CONFIG_HOME='+str(P)+'/').encode()) for x in (q/'environ').read_bytes().split(bytes([0]))):owned.append({'pid':int(q.name),'comm':(q/'comm').read_text().strip()})
 except OSError:pass
for v in owned:
 try:os.kill(v['pid'],15)
 except ProcessLookupError:pass
external=[]
for n,allowed in [('receiver.pid',['receiver.py','controlled_receiver.py']),('notify-monitor.pid',['dbus-monitor'])]:
 f=P/n
 if not f.exists():continue
 pid=int(f.read_text());q=Path('/proc')/str(pid)
 if not q.exists():continue
 args=(q/'cmdline').read_bytes().split(bytes([0]));assert any(x.encode() in args or str(P/x).encode() in args for x in allowed),(n,pid);os.kill(pid,15);external.append(pid)
time.sleep(2)
before=set((P/'packages-before.txt').read_text().splitlines());after=set((P/'packages-after.txt').read_text().splitlines());gained=sorted(after-before-{'putgd'})
for tag,cmd in [('remove-putgd',['sudo','-n','apt-get','remove','-y','putgd']),('purge-gained',['sudo','-n','apt-get','purge','-y',*gained])]:
 if tag=='purge-gained' and not gained:continue
 with (P/(tag+'.log')).open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,(tag,r.returncode)
manualBefore=set((P/'apt-manual-baseline.txt').read_text().splitlines());manualNow=set(subprocess.check_output(['apt-mark','showmanual'],text=True).splitlines());touched={'putgd','python3-pyqt6','python3-gi','python3-gi-cairo','gir1.2-gtk-4.0','python3-pil','python3-numpy','fonts-dejavu-core','chromium'}
for action,pkgs in [('auto',sorted((manualNow-manualBefore)&touched)),('manual',sorted((manualBefore-manualNow)&touched))]:
 if pkgs:subprocess.run(['sudo','-n','apt-mark',action,*pkgs],check=True,stdout=open(P/('apt-mark-'+action+'.log'),'w'))
full=subprocess.check_output(['dpkg-query','-W','-f=${binary:Package} ${Version} ${db:Status-Abbrev}\n'],text=True);(P/'package-status-restored.txt').write_text(full);old=set((P/'package-status-before.txt').read_text().splitlines());now=set(full.splitlines());manualAfter=set(subprocess.check_output(['apt-mark','showmanual'],text=True).splitlines());v={'ownedProcessesTerminated':owned,'externalPidsTerminated':external,'removedNewPackages':gained,'packageVersionsMatch':old==now,'packageVersionsAdded':sorted(now-old),'packageVersionsMissing':sorted(old-now),'manualPackageFlagsMatch':manualBefore==manualAfter,'manualFlagsAdded':sorted(manualAfter-manualBefore),'manualFlagsMissing':sorted(manualBefore-manualAfter),'scaleChanged':False,'notificationSettingsChanged':False,'hotkeyProof':'hotkey-restoration.json'};(P/'cleanup.json').write_text(json.dumps(v,indent=2));print(v,flush=True);assert old==now and manualBefore==manualAfter,'package restoration mismatch'
(P/'physical-restored.done').write_text('done')
