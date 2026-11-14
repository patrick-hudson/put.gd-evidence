#!/usr/bin/env python3
import sys,json,time
from pathlib import Path
import gi
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,GLib,Gio
out=Path(sys.argv[2]);start=time.monotonic()
class Player(Gtk.Application):
 def __init__(self):super().__init__(application_id='org.putgd.SyntheticVideoPlayer',flags=Gio.ApplicationFlags.NON_UNIQUE);self.connect('activate',self.show)
 def show(self,app):
  self.window=Gtk.ApplicationWindow(application=self);self.window.set_title('Sweep exported clip playback');self.window.set_default_size(800,500)
  self.media=Gtk.MediaFile.new_for_filename(sys.argv[1]);self.video=Gtk.Video.new();self.video.set_media_stream(self.media);self.window.set_child(self.video);self.window.present();self.media.play();self.samples=[];GLib.timeout_add(250,self.tick)
 def tick(self):
  err=self.media.get_error();self.samples.append({'at':time.monotonic()-start,'timestampUs':self.media.get_timestamp(),'playing':self.media.get_playing(),'prepared':self.media.is_prepared(),'error':str(err) if err else None});out.write_text(json.dumps(self.samples,indent=2));return True
Player().run([])
