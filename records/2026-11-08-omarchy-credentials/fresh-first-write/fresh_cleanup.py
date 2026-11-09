from pathlib import Path
import common,json
common.RUN=Path('work/lab-runs/o3').resolve()
s=common.call('settings.get')['document'];refs=[p['credentials']['reference'] for p in s['profiles']];assert all(p['provider']=='s3' for p in s['profiles'])
common.call('history.clear');common.patch(dict(profiles=[],captureDefaults=dict(destination='local',profileId=None,publicationMode='default'),actions={a:dict(destination='default',profileId=None,publicationMode='default') for a in ('region','window','desktop','clipboard','edit')}));common.call('logs.clear');common.call('ui.quit')
code="""from gi.repository import Gio,GLib
b=Gio.bus_get_sync(Gio.BusType.SESSION,None)
def p(path,key):return b.call_sync('org.freedesktop.secrets',path,'org.freedesktop.DBus.Properties','Get',GLib.Variant('(ss)',('org.freedesktop.Secret.Item',key)),None,Gio.DBusCallFlags.NONE,3000,None).unpack()[0]
c='/org/freedesktop/secrets/collection/Default_5fkeyring'
a=b.call_sync('org.freedesktop.secrets',c,'org.freedesktop.DBus.Properties','Get',GLib.Variant('(ss)',('org.freedesktop.Secret.Collection','Items')),None,Gio.DBusCallFlags.NONE,3000,None).unpack()[0]
for i in a:
 attrs=p(i,'Attributes');assert attrs.get('server')=='putgd' and attrs.get('user') in REFS
 b.call_sync('org.freedesktop.secrets',i,'org.freedesktop.Secret.Item','Delete',None,None,Gio.DBusCallFlags.NONE,3000,None)
print('removed remaining duplicate-attempt items',len(a))
""".replace('REFS',repr(refs+['putgd/fresh-native','putgd/fresh-s3']))
print(common.shell("python3 - <<'CLEAN'\n"+code+"CLEAN\nbusctl --user get-property org.freedesktop.secrets /org/freedesktop/secrets/collection/Default_5fkeyring org.freedesktop.Secret.Collection Items; pgrep -a -u $(id -u) ^putgd || true"))
p=Path('fresh.py');t=p.read_text().replace('r.type(','qtype.typed(');t=t.replace('time.sleep(.2);qtype.typed(name)','time.sleep(1);qtype.typed(name)');t=t.replace('time.sleep(.3);before=status()', 'time.sleep(.3);assert [p["id"] for p in common.call("settings.get")["document"]["profiles"]]==[name],"destination_input_did_not_match";before=status()');p.write_text(t);compile(t,str(p),'exec')
Path('/home/patrick/work/oc/fresh-first-write/duplicate-attempt-note.txt').write_text('A duplicate native photo attempt after the passing first-write run typed a garbled destination name before the dialog settled. Its lookup of the expected reference therefore failed before any connection test. The original passing JSON and UI witness are retained; duplicate profiles/items removed. The driver now types through QMP and validates the actual destination ID before credential entry. This was an input-driver precondition failure.\n')
