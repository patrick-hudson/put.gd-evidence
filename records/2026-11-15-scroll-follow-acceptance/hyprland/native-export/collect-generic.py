import json,hashlib,tarfile,os,subprocess,shutil,gzip
from pathlib import Path
P=Path.home()/'work/sfa15';files={};index={}
def add(f,arc=None):
 if not f.is_file() or f.is_symlink():return
 arc=arc or str(f.relative_to(P));files[arc]=f
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for prefix in [P,P/'b']:
 label='candidate' if prefix==P else 'nightly'
 if (prefix/'diagnostics.json').exists():
  d=json.loads((prefix/'diagnostics.json').read_text());out=P/(label+'-build-proof.json');out.write_text(json.dumps({'build':d['build'],'diagnosticsSource':str(prefix/'diagnostics.json')},indent=1));add(out)
 for d in (prefix/'runs').glob('*') if (prefix/'runs').exists() else []:
  for f in d.iterdir():
   if f.is_file() and f.suffix in ['.json','.log','.err','.png']:
    index[str(f.relative_to(P))]={'sha256':digest(f),'bytes':f.stat().st_size}
    if f.name not in ['capture.png','reference.png']:add(f)
    elif any(n in d.name for n in ['github','news','jump','stackoverflow']):add(f)
 for n in ['pages-chrome.log','pages-chrome-attempt1.log','pages-ff.log','race.log','race-attempt1.log','toggle-stop-race.json','resident.log','extract.log']:
  add(prefix/n)
for n in ['extra-results.json','extra-run.log','mcp-results.json','lostauto-results.json','lostauto-operation.json','lostauto-run.log','pause-relative-results.log','pause-relative-summary.json','pause-relative-extras.log','pause-results.log','pause-attempt1.log','pause-attempt2.log','resident-attempt1.log','resident-attempt2.log','uv-install.log','uv-remove.log','refs-run.log','python-reference-info.json','wiki-reference-info.json','toggle-stop-race.json','pages-inside.log']:
 add(P/n)
for pattern in ['bar-*.png','inside-*.png','blank-*.png','github-user-persistent-lost.png','click-miss-*.png','login-*.png']:
 for f in P.glob(pattern):add(f)
for n in ['relative-control.py','extra-relative.py','lostauto-relative.py','trial-first-motion.py','pages-before-current-viewport.py','calibrate-relative.py','calibrate-m74.py','inside-click.py','gnome-ext.py','pause-baseline.py','pause-summary.py','baseline-prepare.py','accept.py','pages.py','pause.py','pause-relative.py','trial.py','trial_relative.py','extra.py','lostauto.py','refs.py','race.py','baseline-race.py','umouse.py','ukey.py','live7.py','rfb.py','score.py','scroll_tracker_score.py','blank.html']:
 add(P/n,'scripts/'+n)
notice=[]
for f in (P/'s').rglob('*.jsonl'):
 for line in f.read_text(errors='replace').splitlines():
  if 'scroll_blank_stretch' in line:notice.append(json.loads(line))
out=P/'blank-notice-log.json';out.write_text(json.dumps(notice,indent=1));add(out)
identity={'osRelease':Path('/etc/os-release').read_text(),'packages':subprocess.run(['rpm','-q','plasma-workspace','kwin','gnome-shell','mutter'] if shutil.which('rpm') else ['dpkg-query','-W','cinnamon','muffin','plasma-workspace','kwin-wayland'],capture_output=True,text=True).stdout,'candidateAppImageSha256':digest(P/'candidate.AppImage'),'nightlyAppImageSha256':digest(P/'nightly.AppImage') if (P/'nightly.AppImage').exists() else None,'candidateBinaries':{n:digest(P/'squashfs-root/usr/bin'/n) for n in ['putgd','putgd-cli','putgd-record']},'socketPaths':{str((root/'r/putgd/session.sock').resolve()):len(str((root/'r/putgd/session.sock').resolve()).encode()) for root in [P,P/'b']}}
out=P/'host-and-package-proof.json';out.write_text(json.dumps(identity,indent=1));add(out)
out=P/'restore-index.json';out.write_text(json.dumps({'root':str(P),'files':index,'note':'Original full-resolution passed images and every test source remain private on this builder. Published packet contains the result JSON, helper logs, native state pictures and difficult-page images.'},indent=1));add(out)
for prefix in [P,P/'b']:
 if (prefix/'helper.log').exists():
  with (prefix/'helper.log').open('rb') as source,gzip.open(prefix/'helper-complete.log.gz','wb') as target:shutil.copyfileobj(source,target)
  add(prefix/'helper-complete.log.gz')
 for f in prefix.glob('trial-*.log'):add(f)
 for f in prefix.glob('*.summary.json'):add(f)
 for f in prefix.glob('extra-*-attempt.log'):add(f)
for n in ['gnome-before.json','gnome-restored.json','gnome-health.jsonl','cinnamon-acceleration-before.json','pages-jump.log','pages-news.log','protocol-checks.json','lostauto-capture.png','lostauto-result.json','inside-cancel-paused.json','inside-click-results.json','inside-click.log','fixed8-failure.log','control-history-staging-audit.json','relative-calibration.json','relative-calibration.log','pointer-load.json','mixed-comparison-info.json','mixed-capture.png','mixed-reference.png']:
 add(P/n)
for d in [*P.glob('harness-attempt*'),*P.glob('functional-attempt*'),*P.glob('functional-key-focus-attempt*'),*P.glob('page-geometry-attempt*'),*P.glob('focused-user-attempt*'),*P.glob('recovery-attempt*'),*P.glob('control-audit-attempt*'),*P.glob('gnome-ext24*'),*P.glob('gnome-ext23*'),P/'supplement-admission-attempt1',P/'keyboard-candidate',P/'doneproof-settings-attempt1']:
 for f in d.rglob('*'):
  if f.is_file() and f.suffix in ['.json','.log','.png','.md','.py']:add(f)
for prefix in [P,P/'b']:
 for n in ['supplement-process-results.json','nightly-extension-proof.json','baseline-prepare.log','pause23.log','pause23.summary.json','extension23-relogin.log','extension23-files24.log','candidate23-start.log','baseline-gnome-pointer.log','baseline-gnome-pointer.summary.json','doneproof2-pages.log','doneproof2-news.log','close-settings.log']:
  add(prefix/n)
 for pattern in ['gnome*.log','mcp-runtime-proof.json','keyboard-probe*','keyboard-capture-probe.*','keyboard-*-capture-helper.log','keyboard-*.png','user-script-recovery-*','auto-script-recovery-*','mixed-focused-*','native-viewport-offset.json','page-geometry-interrupt.json','pointer-witness-*.json','extension-*.txt','pointer-*.json','pointer-*.png','pointer-*.log','before-click.jsonl','full-region-*.json','full-region-*.png','full-region-*.log','scroll-from-top-comparison-setting.json','local-only-settings-proof.json','control-*.json','control-*.log','user-recovered-*.png','user-recovered-*.json','user-focused-*','start-*.log','resident-initial.log','lostauto-*reference*.png','lostauto-*reference*.json','post*.log','mcp-retry*.json','mcp-retry*.log']:
  for f in prefix.glob(pattern):add(f)
for n in ['close-settings.py','baseline-gnome-pointer.py','find_history.py','keyboard-capture-probe.py','user-script-recovery.py','auto-script-recovery.py','mixed-focused.py','collect-recovery.py','keyboard-probe.py','ukey-ready.py','user-focused.py','lostauto-focused.py','relative-control-native.py','pointer-witness.py','pointer-witness.js','trial-native-pointer.py','pages-relative.py','proof-local.py','baseline-pointer.py','baseline-no-inside.py','adjust-baseline.py','mcptest.py','audit-controls.py','retry-control-audit.py','collect-lostauto.py','cleanup-generic.py','collect-generic.py']:
 add(P/n,'scripts/'+n)
with tarfile.open(P/'desktop-evidence.tar.gz','w:gz') as t:
 for name,f in sorted(files.items()):t.add(f,arcname=name)
print('files',len(files),'packetBytes',(P/'desktop-evidence.tar.gz').stat().st_size,'sha256',digest(P/'desktop-evidence.tar.gz'))
