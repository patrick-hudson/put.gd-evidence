#!/bin/sh
set -eu
# Run on the chosen Linux builder, beside kwin.c, with system development packages.
wayland-scanner client-header /usr/share/plasma-wayland-protocols/fake-input.xml fake.h
wayland-scanner private-code /usr/share/plasma-wayland-protocols/fake-input.xml fake.c
wayland-scanner client-header /usr/share/plasma-wayland-protocols/zkde-screencast-unstable-v1.xml cast.h
wayland-scanner private-code /usr/share/plasma-wayland-protocols/zkde-screencast-unstable-v1.xml cast.c
cc kwin.c fake.c cast.c -o kwin $(pkg-config --cflags --libs wayland-client)
