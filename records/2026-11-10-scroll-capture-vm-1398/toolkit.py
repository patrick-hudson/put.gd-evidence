import os
os.environ.update(GTK_A11Y="none", NO_AT_BRIDGE="1", QT_ACCESSIBILITY="0", QT_LINUX_ACCESSIBILITY_ALWAYS_ON="0")
import sys,json
kind=sys.argv[1];text='\n'.join(f'Row {i:04d} — standalone scroll probe' for i in range(1500))
if kind=='qt':
 from PyQt6.QtWidgets import QApplication,QPlainTextEdit
 a=QApplication([]);w=QPlainTextEdit();w.setPlainText(text);w.setReadOnly(True);w.setWindowTitle('Scroll probe Qt text');w.verticalScrollBar().valueChanged.connect(lambda v:print(json.dumps({'kind':'qt','scrollbar':v}),flush=True));w.showMaximized();a.exec()
else:
 import gi
 gi.require_version('Gtk','4.0');from gi.repository import Gtk,GLib
 Gtk.init();w=Gtk.Window(title='Scroll probe GTK4 text');s=Gtk.ScrolledWindow();t=Gtk.TextView();t.get_buffer().set_text(text);t.set_editable(False);t.set_cursor_visible(False);s.set_child(t);w.set_child(s);s.get_vadjustment().connect('value-changed',lambda adj:print(json.dumps({'kind':'gtk4','y':adj.get_value()}),flush=True));w.maximize();w.present();GLib.MainLoop().run()
