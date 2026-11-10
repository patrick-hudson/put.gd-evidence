from pathlib import Path
p=Path('/home/patrick/work/pg-cd/src/platform/wayland/SurfaceVisibility.cpp');s=p.read_text();Path('/tmp/pg-r2-valid-visibility.cpp').write_text(s)
s=s.replace('display_=connection.connect();','const auto socket=qgetenv("WAYLAND_SOCKET");qunsetenv("WAYLAND_SOCKET");CaptureConnection wrong;\n  if(!socket.isNull())qputenv("WAYLAND_SOCKET",socket);display_=wrong.connect();')
p.write_text(s)
