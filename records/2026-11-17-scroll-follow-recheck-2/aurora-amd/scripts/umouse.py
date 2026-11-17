#!/usr/bin/env python3
"""A relative USB-like mouse with a wheel, through /dev/uinput, as a real mouse moves.

Reads lines on stdin: "m DX DY" moves, "w N" turns the wheel N notches (positive:
the page goes down), "d" / "u" left button down / up, "q" quits. Prints "ready NAME".
Lab input only (#1515, after the evidence record 2026-11-14-scroll-pointer-release-1514).
"""
import fcntl, os, struct, sys, time

UI_SET_EVBIT, UI_SET_KEYBIT, UI_SET_RELBIT = 0x40045564, 0x40045565, 0x40045566
UI_DEV_SETUP, UI_DEV_CREATE, UI_DEV_DESTROY = 0x405C5503, 0x5501, 0x5502
EV_SYN, EV_KEY, EV_REL = 0, 1, 2
REL_X, REL_Y, REL_WHEEL, REL_WHEEL_HI_RES = 0, 1, 8, 11
BTN_LEFT, BTN_RIGHT = 0x110, 0x111
NAME = b'putgd-lab relative mouse with wheel'


def emit(fd, kind, code, value):
    os.write(fd, struct.pack('llHHi', 0, 0, kind, code, value))


def main():
    fd = os.open('/dev/uinput', os.O_WRONLY | os.O_NONBLOCK)
    for bit in (EV_KEY, EV_REL):
        fcntl.ioctl(fd, UI_SET_EVBIT, bit)
    for key in (BTN_LEFT, BTN_RIGHT):
        fcntl.ioctl(fd, UI_SET_KEYBIT, key)
    for rel in (REL_X, REL_Y, REL_WHEEL, REL_WHEEL_HI_RES):
        fcntl.ioctl(fd, UI_SET_RELBIT, rel)
    fcntl.ioctl(fd, UI_DEV_SETUP, struct.pack('HHHH80sI', 0x03, 0x1234, 0x5679, 1, NAME, 0))
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
            elif parts[0] == 'w':
                n = int(parts[1])
                # evdev: a positive wheel value scrolls up, away from the user.
                for _ in range(abs(n)):
                    emit(fd, EV_REL, REL_WHEEL, -1 if n > 0 else 1)
                    emit(fd, EV_REL, REL_WHEEL_HI_RES, -120 if n > 0 else 120)
                    emit(fd, EV_SYN, 0, 0)
                    time.sleep(float(os.environ.get('SFR_WHEEL_DELAY','0.012')))
                continue
            elif parts[0] in ('d', 'u'):
                emit(fd, EV_KEY, BTN_LEFT, 1 if parts[0] == 'd' else 0)
            emit(fd, EV_SYN, 0, 0)
    finally:
        fcntl.ioctl(fd, UI_DEV_DESTROY)
        os.close(fd)


if __name__ == '__main__':
    main()
