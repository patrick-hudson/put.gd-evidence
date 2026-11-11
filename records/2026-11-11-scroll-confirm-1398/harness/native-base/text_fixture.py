# Native text views with a long file of near-identical lines, as in the VM
# acceptance round: `qt` is a QPlainTextEdit, `gtk` a GTK 4 GtkTextView.
# Prints the scroll position on every change.
import os, sys, json, time
os.environ.update(GTK_A11Y="none", NO_AT_BRIDGE="1", QT_ACCESSIBILITY="0", QT_LINUX_ACCESSIBILITY_ALWAYS_ON="0")
kind = sys.argv[1]
lines = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
text = '\n'.join(f'Row {i:04d} — standalone scroll probe' for i in range(lines))
if kind == 'qt':
    from PyQt6.QtWidgets import QApplication, QPlainTextEdit
    a = QApplication([]); w = QPlainTextEdit(); w.setFrameShape(QPlainTextEdit.Shape.NoFrame); w.setPlainText(text); w.setReadOnly(True); w.setWindowTitle('put.gd sf1398 Qt text')
    w.verticalScrollBar().valueChanged.connect(lambda v: print(json.dumps({'kind': 'qt', 'scrollbar': v, 't': round(time.monotonic(), 3)}), flush=True))
    w.showFullScreen();
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(1000, lambda: w.verticalScrollBar().setValue(w.verticalScrollBar().maximum()))
    print("ready", flush=True); a.exec()
else:
    import gi
    gi.require_version('Gtk', '4.0'); from gi.repository import Gtk, GLib
    Gtk.init(); w = Gtk.Window(title='put.gd sf1398 GTK4 text'); s = Gtk.ScrolledWindow(); t = Gtk.TextView(); t.get_buffer().set_text(text); t.set_editable(False); t.set_cursor_visible(False); s.set_child(t); w.set_child(s)
    s.get_vadjustment().connect('value-changed', lambda adj: print(json.dumps({'kind': 'gtk4', 'y': adj.get_value(), 't': round(time.monotonic(), 3)}), flush=True))
    w.fullscreen(); w.present();
    GLib.timeout_add(1000, lambda: (s.get_vadjustment().set_value(s.get_vadjustment().get_upper()), False)[1])
    print("ready", flush=True); GLib.MainLoop().run()
