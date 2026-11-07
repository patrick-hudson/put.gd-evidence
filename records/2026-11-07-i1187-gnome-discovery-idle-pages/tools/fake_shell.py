#!/usr/bin/env python3
"""Stand-in org.gnome.Shell for headless put.gd GNOME-adapter memory runs on a private session bus.
Owns org.gnome.Shell. The put.gd extension object is absent until SIGUSR1 (export + CapabilitiesChanged,
as integrations/gnome/extension.js enable() does); SIGUSR2 disables it (CapabilitiesChanged + unexport).
--enabled starts with the object exported. Every Hello is logged with a monotonic timestamp to the log file,
and UnknownObject replies are counted too (method calls to the absent path)."""
import json, signal, sys, time
from gi.repository import Gio, GLib
IFACE = 'org.putgd.Gnome50'; PATH = '/org/gnome/Shell/Extensions/Putgd'
METHODS = {'Hello': 0, 'SetUiProcess': 1, 'InvalidateCopy': 0, 'Revision': 0, 'Prepare': 2, 'Preview': 2, 'Acquire': 2, 'Read': 3,
           'Release': 1, 'BeginCopy': 3, 'WriteCopy': 3, 'CommitCopy': 1, 'Bind': 1, 'SelectArea': 1, 'ShowRecordingFrame': 1, 'HideRecordingFrame': 0}
XML = f'''<node><interface name="{IFACE}">
<method name="Hello"><arg type="s" direction="out"/></method>
<method name="SetUiProcess"><arg type="u" direction="in"/><arg type="s" direction="out"/></method>
<method name="InvalidateCopy"><arg type="s" direction="out"/></method>
<method name="Revision"><arg type="s" direction="out"/></method>
<method name="Prepare"><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="s" direction="out"/></method>
<method name="Preview"><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="s" direction="out"/></method>
<method name="Acquire"><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="s" direction="out"/></method>
<method name="Read"><arg type="s" direction="in"/><arg type="t" direction="in"/><arg type="u" direction="in"/><arg type="s" direction="out"/></method>
<method name="Release"><arg type="s" direction="in"/><arg type="s" direction="out"/></method>
<method name="BeginCopy"><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="t" direction="in"/><arg type="s" direction="out"/></method>
<method name="WriteCopy"><arg type="s" direction="in"/><arg type="t" direction="in"/><arg type="s" direction="in"/><arg type="s" direction="out"/></method>
<method name="CommitCopy"><arg type="s" direction="in"/><arg type="s" direction="out"/></method>
<method name="Bind"><arg type="s" direction="in"/><arg type="s" direction="out"/></method>
<method name="SelectArea"><arg type="s" direction="in"/><arg type="s" direction="out"/></method>
<method name="ShowRecordingFrame"><arg type="s" direction="in"/><arg type="s" direction="out"/></method>
<method name="HideRecordingFrame"><arg type="s" direction="out"/></method>
<signal name="Action"><arg type="s"/><arg type="s"/></signal>
<signal name="ClipboardChanged"><arg type="t"/></signal>
<signal name="CapabilitiesChanged"/>
</interface></node>'''
log = open(sys.argv[1], 'a', buffering=1)
def note(event, **kw): log.write(json.dumps({'t': round(time.monotonic(), 3), 'event': event, **kw}) + '\n')
node = Gio.DBusNodeInfo.new_for_xml(XML).interfaces[0]
conn = Gio.bus_get_sync(Gio.BusType.SESSION, None)
reg = [0]
def call(connection, sender, path, iface, method, params, invocation):
    note('call', method=method, sender=sender)
    if method == 'Hello':
        out = {'version': 1, 'shellMajor': 50, 'extensionVersion': 1, 'clipboardRevision': 1, 'uiProcessVersion': 1, 'recordingVersion': 1, 'previewVersion': 1}
    elif method == 'Bind':
        req = json.loads(params.unpack()[0])
        out = {'bindings': {a: {'requested': str((req.get(a) or {}).get('requested', '')), 'bound': False, 'error': 'shortcut_unsupported'} for a in ('region', 'window', 'desktop', 'clipboard', 'edit', 'record')}}
    else:
        out = {'error': {'code': 'helper_unavailable', 'message': 'stand-in Shell', 'details': {}}}
    invocation.return_value(GLib.Variant('(s)', (json.dumps(out),)))
def enable():
    if reg[0]: return
    reg[0] = conn.register_object(PATH, node, call, None, None)
    conn.emit_signal(None, PATH, IFACE, 'CapabilitiesChanged', None); conn.flush_sync(None); note('enabled')
def disable():
    if not reg[0]: return
    conn.emit_signal(None, PATH, IFACE, 'CapabilitiesChanged', None); conn.unregister_object(reg[0]); reg[0] = 0; conn.flush_sync(None); note('disabled')
# Count calls to the absent object: a filter sees every incoming message to this connection.
def filt(connection, message, incoming):
    if incoming and message.get_message_type() == Gio.DBusMessageType.METHOD_CALL and message.get_path() == PATH and not reg[0]:
        GLib.idle_add(lambda m=message.get_member(): note('absent_call', method=m) and False)
    return message
conn.add_filter(filt)
owner = Gio.bus_own_name_on_connection(conn, 'org.gnome.Shell', Gio.BusNameOwnerFlags.NONE, lambda *a: note('owned'), lambda *a: note('lost'))
if '--enabled' in sys.argv: enable()
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR1, lambda: enable() or True)
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR2, lambda: disable() or True)
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, lambda: loop.quit() or False)
loop = GLib.MainLoop(); loop.run()
