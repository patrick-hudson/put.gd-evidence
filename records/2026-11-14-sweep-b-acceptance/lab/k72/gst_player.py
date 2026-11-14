#!/usr/bin/env python3
"""Independent GTK3/GStreamer player for an exported synthetic clip."""
import sys,json,time
from pathlib import Path
import gi
gi.require_version('Gtk','3.0');gi.require_version('Gst','1.0')
from gi.repository import Gtk,Gst,GLib
Gst.init(None);out=Path(sys.argv[2]);samples=[];errors=[];began=time.monotonic()
w=Gtk.Window(title='Sweep exported clip playback');w.set_default_size(800,500)
p=Gst.ElementFactory.make('playbin');sink=Gst.ElementFactory.make('gtksink');assert p and sink,'Player or gtksink unavailable'
p.props.uri=Path(sys.argv[1]).as_uri();p.props.video_sink=sink;p.props.audio_sink=Gst.ElementFactory.make('fakesink');w.add(sink.props.widget);w.show_all()
bus=p.get_bus();bus.add_signal_watch()
def message(b,m):
 if m.type==Gst.MessageType.ERROR:errors.append(str(m.parse_error()[0]))
bus.connect('message',message);p.set_state(Gst.State.PLAYING)
def tick():
 okay,pos=p.query_position(Gst.Format.TIME);samples.append({'at':time.monotonic()-began,'timestampUs':pos//1000 if okay else 0,'error':errors[-1] if errors else None});out.write_text(json.dumps(samples,indent=2));return True
GLib.timeout_add(250,tick)
w.connect('destroy',lambda *_:Gtk.main_quit());Gtk.main();p.set_state(Gst.State.NULL)
