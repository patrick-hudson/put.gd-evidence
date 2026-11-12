# The final pass's v3text.py with a third argument "bottom": the view opens scrolled to its end.
import os,sys,json,time
os.environ.update(GTK_A11Y='none',NO_AT_BRIDGE='1',QT_ACCESSIBILITY='0')
kind=sys.argv[1];width=int(sys.argv[2]);bottom=len(sys.argv)>3 and sys.argv[3]=='bottom';text='\n'.join(f'Row {i:04d} — standalone scroll probe' for i in range(1500))
if kind=='qt':
 from PyQt6.QtWidgets import QApplication,QWidget,QPlainTextEdit
 from PyQt6.QtCore import Qt,QTimer
 a=QApplication([]);w=QWidget();w.setWindowTitle('VM2 Qt text 1500 lines');t=QPlainTextEdit(w);t.setGeometry(0,0,width,1080);t.setPlainText(text);t.setReadOnly(True);t.setFrameShape(QPlainTextEdit.Shape.NoFrame);t.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);t.verticalScrollBar().valueChanged.connect(lambda v:print(json.dumps({'line':v,'time':time.time()}),flush=True));w.showFullScreen()
 if bottom:QTimer.singleShot(800,lambda:t.verticalScrollBar().setValue(t.verticalScrollBar().maximum()))
 print('ready',flush=True);a.exec()
else:
 import gi
 gi.require_version('Gtk','4.0');from gi.repository import Gtk,GLib
 Gtk.init();w=Gtk.Window(title='VM2 GTK4 text 1500 lines');fixed=Gtk.Fixed();w.set_child(fixed);s=Gtk.ScrolledWindow();s.set_size_request(width,600);fixed.put(s,0,100);t=Gtk.TextView();t.get_buffer().set_text(text);t.set_editable(False);t.set_cursor_visible(False);s.set_child(t);s.get_vadjustment().connect('value-changed',lambda a:print(json.dumps({'y':a.get_value(),'time':time.time()}),flush=True));w.fullscreen();w.present()
 if bottom:
  def end():
   adj=s.get_vadjustment();adj.set_value(adj.get_upper()-adj.get_page_size());return False
  GLib.timeout_add(1500,end)
 print('ready',flush=True);GLib.MainLoop().run()
