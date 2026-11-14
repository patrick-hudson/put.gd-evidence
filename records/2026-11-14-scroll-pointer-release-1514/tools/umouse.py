#!/usr/bin/env python3
"""A relative USB-like mouse through /dev/uinput, as a real mouse moves (root).

Reads lines on stdin: "m DX DY" moves, "d" / "u" left button down / up, "q" quits.
Prints "ready NAME" once the device exists.
"""
import fcntl
import os
import struct
import sys
import time

UI_SET_EVBIT, UI_SET_KEYBIT, UI_SET_RELBIT = 0x40045564, 0x40045565, 0x40045566
UI_DEV_SETUP, UI_DEV_CREATE, UI_DEV_DESTROY = 0x405C5503, 0x5501, 0x5502
EV_SYN, EV_KEY, EV_REL = 0, 1, 2
REL_X, REL_Y, BTN_LEFT, BTN_RIGHT = 0, 1, 0x110, 0x111
NAME = b'putgd-lab relative mouse'


def emit(fd, kind, code, value):
    os.write(fd, struct.pack('llHHi', 0, 0, kind, code, value))


def main():
    fd = os.open('/dev/uinput', os.O_WRONLY | os.O_NONBLOCK)
    fcntl.ioctl(fd, UI_SET_EVBIT, EV_KEY)
    fcntl.ioctl(fd, UI_SET_EVBIT, EV_REL)
    fcntl.ioctl(fd, UI_SET_KEYBIT, BTN_LEFT)
    fcntl.ioctl(fd, UI_SET_KEYBIT, BTN_RIGHT)
    fcntl.ioctl(fd, UI_SET_RELBIT, REL_X)
    fcntl.ioctl(fd, UI_SET_RELBIT, REL_Y)
    fcntl.ioctl(fd, UI_DEV_SETUP, struct.pack('HHHH80sI', 0x03, 0x1234, 0x5678, 1, NAME, 0))
    fcntl.ioctl(fd, UI_DEV_CREATE)
    time.sleep(1.0)
    print('ready', NAME.decode(), flush=True)
    try:
        for line in sys.stdin:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == 'q':
                break
            if parts[0] == 'm':
                emit(fd, EV_REL, REL_X, int(parts[1]))
                emit(fd, EV_REL, REL_Y, int(parts[2]))
            elif parts[0] in ('d', 'u'):
                emit(fd, EV_KEY, BTN_LEFT, 1 if parts[0] == 'd' else 0)
            emit(fd, EV_SYN, 0, 0)
    finally:
        fcntl.ioctl(fd, UI_DEV_DESTROY)
        os.close(fd)


if __name__ == '__main__':
    main()
