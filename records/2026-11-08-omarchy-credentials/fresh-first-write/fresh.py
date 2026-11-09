from pathlib import Path
from tools.lab import lab
from tools.lab.rfb import RFB
from tools.lab.provision_live_credentials import read_private_credentials
from tools.lab.surface_driver.fixtures.live_outcomes import key_set_two
import common,qtype,json,time,sys,base64
RUN=Path('/home/patrick/work/oc/src/work/lab-runs/o3');common.RUN=RUN;qtype.r=RUN
native=len(sys.argv)>1;name='fresh-native' if native else 'fresh-s3';app='/usr/bin/putgd' if native else '/home/lab/current.AppImage'
out=Path('/home/patrick/work/oc/fresh-first-write');out.mkdir(exist_ok=True)
def status():return common.shell('busctl --user get-property org.freedesktop.secrets /org/freedesktop/secrets/collection/Default_5fkeyring org.freedesktop.Secret.Collection Locked').strip()
initial=status()
if not native:
 lab.put(RUN,'/home/patrick/work/oc/packages/current.AppImage',app);lab.ssh(RUN,'chmod 700 '+app)
common.shell('(setsid -f '+app+' --history > /tmp/oc-fresh-app.log 2>&1 < /dev/null)');time.sleep(5)
r=RFB(5942);r.click(640,65);r.click(105,714);time.sleep(.2);r.click(130,608);time.sleep(1);qtype.typed(name);r.key('ret');time.sleep(.5);r.click(681,416);qtype.typed('put.gd');r.key('tab');time.sleep(.5);r.click(650,489);r.key('ctrl','a');qtype.typed('us-east-2');r.key('tab');time.sleep(.5);r.click(670,541);r.key('ctrl','a');qtype.typed('acceptance/oc-'+name+'-20261109/');r.key('tab');time.sleep(.5)
for _ in range(7):r.scroll(1120,620,-1);time.sleep(.05)
r.click(720,306);r.key('end');r.key('ret');time.sleep(.4)
for _ in range(15):r.scroll(1120,620,-1);time.sleep(.04)
time.sleep(.3);assert [p["id"] for p in common.call("settings.get")["document"]["profiles"]]==[name],"destination_input_did_not_match";before=status();r.screenshot(str(out/(name+'-before.png')))
v=key_set_two(read_private_credentials(Path.home()/'Documents/creds.txt'))['credentials'];r.click(681,424);qtype.typed(v['accessKey']);r.click(684,478);qtype.typed(v['secretKey']);r.click(745,634);time.sleep(1)
x=json.loads(base64.b64decode(common.shell('secret-tool lookup user putgd/'+name+' server putgd')));assert all(x[k]==v[k] for k in v),'credential_keyboard_mismatch'
after=status();r.click(920,685);time.sleep(5);RFB(5942).screenshot(str(out/(name+'-tested.png')))
common.setup('testDestination',name)
summary=dict(package='Arch' if native else 'AppImage',run=lab.state(RUN),initialLocked=initial,lockedImmediatelyBeforeProductStore=before,lockedAfterProductStore=after,keyboardValuesVerified=True,connectionPassed=True,preparation='No secret-tool writes, keyring imports, or keyring preparation before product Save')
(out/(name+'.json')).write_text(json.dumps(summary,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='run'}),flush=True)
common.patch(dict(profiles=[],captureDefaults=dict(destination='local',profileId=None,publicationMode='default'),actions={a:dict(destination='default',profileId=None,publicationMode='default') for a in ('region','window','desktop','clipboard','edit')}));common.call('ui.quit');common.shell('secret-tool clear user putgd/'+name+' server putgd; sync')
print('profile and keychain item removed',flush=True)
