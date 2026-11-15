// Acceptance-only observer. No input, signal hooks or changes to production.
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
const XML='<node><interface name="org.putgd.PointerWitness"><method name="Get"><arg type="s" direction="out"/></method></interface></node>';
export default class PointerWitness extends Extension {
 enable(){this._dbus=Gio.DBusExportedObject.wrapJSObject(XML,this);this._dbus.export(Gio.DBus.session,'/org/putgd/PointerWitness');}
 disable(){this._dbus?.unexport();this._dbus=null;}
 Get(){const [x,y]=global.get_pointer();return JSON.stringify({x,y,t:Math.floor(GLib.get_monotonic_time()/1000)});}
}
