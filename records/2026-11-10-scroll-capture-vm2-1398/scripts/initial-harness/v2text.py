import os,sys,json,time
os.environ.update(GTK_A11Y='none',NO_AT_BRIDGE='1',QT_ACCESSIBILITY='0')
kind=sys.argv[1];text='\n'.join(f'Row {i:04d} — standalone scroll probe' for i in range(1500))
if kind=='qt':
 from PyQt6.QtWidgets import QApplication,QWidget,QPlainTextEdit
 from PyQt6.QtCore import Qt
 a=QApplication([]);w=QWidget();w.setWindowTitle('VM2 Qt text 1500 lines');t=QPlainTextEdit(w);t.setGeometry(100,100,960,600);t.setPlainText(text);t.setReadOnly(True);t.setFrameShape(QPlainTextEdit.Shape.NoFrame);t.verticalScrollBar().valueChanged.connect(lambda v:print(json.dumps({'line':v,'time':time.time()}),flush=True));w.showFullScreen();print('ready',flush=True);a.exec()
else:
 import gi
 gi.require_version('Gtk','4.0');from gi.repository import Gtk,GLib
 Gtk.init();w=Gtk.Window(title='VM2 GTK4 text 1500 lines');fixed=Gtk.Fixed();w.set_child(fixed);s=Gtk.ScrolledWindow();s.set_size_request(960,600);fixed.put(s,100,100);t=Gtk.TextView();t.get_buffer().set_text(text);t.set_editable(False);t.set_cursor_visible(False);s.set_child(t);s.get_vadjustment().connect('value-changed',lambda a:print(json.dumps({'y':a.get_value(),'time':time.time()}),flush=True));w.fullscreen();w.present();print('ready',flush=True);GLib.MainLoop().run()
