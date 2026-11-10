import sys,json,hashlib,shlex,tarfile
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
r=Path('/home/patrick/work/pg-cd/work/lab-runs/bc9');o=r/'accept'
lab.verify_owned_guest(r)
bundle=Path('/tmp/pg-c-final-stack-tests.tar')
with tarfile.open(bundle) as archive:
 assert all(x.name in ('test_budgie_labwc','putgd-session-lock-fixture','putgd-labwc-fixture','putgd-region','putgd-clipboard-keeper') and x.isfile() for x in archive.getmembers())
(o/'protocol-bundle-sha256.txt').write_text(hashlib.sha256(bundle.read_bytes()).hexdigest()+'\n')
lab.put(r,bundle,'/tmp/pgct.tar')
lab.ssh(r,'test ! -e /tmp/pgbu; install -d -m 700 /tmp/pgbu; tar -xf /tmp/pgct.tar -C /tmp/pgbu')
(o/'protocol-runtime.txt').write_text(lab.ssh(r,'rpm -q qt6-qtbase labwc; ldd /tmp/pgbu/test_budgie_labwc'))
wrapper='''import os,sys,json,urllib.parse
paths=['/tmp/pgbu','/tmp/pgl-000000/wayland-0','/tmp/pgl-000000/wrong-compositor','/tmp/pgl-000000/putgd/session.sock','/tmp/pg-vis-000000/display','/tmp/pg-peer-000000/display','/run/dbus/system_bus_socket']
for address in os.environ.get('DBUS_SESSION_BUS_ADDRESS','').split(';'):
 if address.startswith('unix:'):
  for field in address[5:].split(','):
   key,_,value=field.partition('=')
   if key in ('path','abstract'):paths.append(urllib.parse.unquote(value))
sizes={p:len(p.encode()) for p in paths};assert all(v<=107 for v in sizes.values())
print(json.dumps({'preflightSocketBytes':sizes,'temporarySuffix':'QTemporaryDir six-character suffix; representative equal-length names checked before test launch'}),flush=True)
os.execv(sys.argv[1],sys.argv[1:])
'''
local=o/'protocol-preflight-and-run.py';local.write_text(wrapper);lab.put(r,local,'/tmp/pgbu/preflight.py')
methods=['visibilityRefusesFullConnectionBacklogWithoutBlocking','visibilityAllowsSlowCompositorSetup','visibilityUsesCaptureCompositor','anonymousInheritedConnectionRefusesRatherThanProbingAnotherSession','captureConnectionReconnectsOnlyAfterPixelConnectionLoss','countdownLockQueryUsesVisibility','lockedWindowAfterFreezeIsRefused','lockDuringCopyIsRefused','lockedDesktopCaptureIsRefused']
command='cd /tmp/pgbu; XDG_RUNTIME_DIR=/tmp/pgbu QT_QPA_PLATFORM=offscreen dbus-run-session -- python3 /tmp/pgbu/preflight.py /tmp/pgbu/test_budgie_labwc '+shlex.join(methods)+' > /tmp/pgbu/protocol-tests.log 2>&1; result=$?; cat /tmp/pgbu/protocol-tests.log; exit $result'
try:
 result=lab.ssh(r,command,timeout=120)
 (o/'protocol-tests.log').write_text(result);print(result,flush=True)
 assert '0 failed, 0 skipped' in result
except Exception:
 (o/'protocol-tests-attempt.log').write_text(lab.ssh(r,'cat /tmp/pgbu/protocol-tests.log 2>/dev/null || true'));raise
