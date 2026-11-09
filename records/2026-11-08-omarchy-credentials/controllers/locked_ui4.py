from common import *
from tools.lab.rfb import RFB
from qtype import typed
import secrets
password=secrets.token_hex(8)
def keyring(old,new,lock=False):
 code='''from gi.repository import Gio,GLib
b=Gio.bus_get_sync(Gio.BusType.SESSION,None)
def c(i,m,s,a,t):return b.call_sync('org.freedesktop.secrets','/org/freedesktop/secrets',i,m,GLib.Variant(s,a),GLib.VariantType(t),Gio.DBusCallFlags.NONE,5000,None).unpack()
i='org.freedesktop.Secret.Service'
s=c(i,'OpenSession','(sv)',('plain',GLib.Variant('s','')),'(vo)')[1]
p=c(i,'ReadAlias','(s)',('default',),'(o)')[0]
c('org.gnome.keyring.InternalUnsupportedGuiltRiddenInterface','ChangeWithMasterPassword','(o(oayays)(oayays))',(p,(s,b'',OLD.encode(),'text/plain'),(s,b'',NEW.encode(),'text/plain')),'()')
if LOCK:c(i,'Lock','(ao)',([p],),'(aoo)')
print('changed synthetic keyring password; stock collection preserved')
'''.replace('OLD',repr(old)).replace('NEW',repr(new)).replace('LOCK',repr(lock))
 shell("python3 - <<'PYKEY'\n"+code+"PYKEY\n")
keyring('',password,True)
call('ui.quit');time.sleep(1);shell('(setsid -f /usr/bin/putgd --history > /tmp/oc-encrypted-start.log 2>&1 < /dev/null)');time.sleep(4)
r=RFB(5940);r.screenshot('/home/patrick/work/oc/locked4-startup-prompt.png');r.key('esc');time.sleep(1);r.click(640,65)
for _ in range(35):r.scroll(1120,620,-1);time.sleep(.04)
time.sleep(.5);r.screenshot('/home/patrick/work/oc/locked4-before.png');r.click(914,634);time.sleep(1);r.screenshot('/home/patrick/work/oc/locked4-prompt.png');r.key('esc');time.sleep(1);r.screenshot('/home/patrick/work/oc/locked4-cancel.png');print('fresh resident, startup and UI prompt cancellation photographed',flush=True)
flag=Path('/home/patrick/work/oc/lock-next4')
for _ in range(150):
 if flag.exists():break
 time.sleep(.1)
s=call('settings.get');j=call('setup.unlockCredentials',dict(profileId='oc-native',expectedRevision=s['metadata']['observedRevision']));time.sleep(1);typed(password);lab.key(RUN,['ret'])
for _ in range(40):
 v=call('setup.inspect',dict(id=j['setupId']))
 if v['state']!='running':break
 time.sleep(.5)
assert v['state']=='completed','unlock_not_completed'
keyring(password,'');setup('testDestination','oc-native');r.screenshot('/home/patrick/work/oc/locked4-unlocked.png')
Path('/home/patrick/work/oc/locked4-result.json').write_text(json.dumps(dict(variant='stock collection temporarily password-protected, restored to blank',freshResident=True,promptVisible=True,cancelled=True,unlockSucceeded=True,connectionAfterUnlock=True)))
print('fresh resident visible unlock and connection passed; blank default restored',flush=True)
