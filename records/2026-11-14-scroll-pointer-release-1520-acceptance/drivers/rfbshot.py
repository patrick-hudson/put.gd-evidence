#!/usr/bin/env python3
"""Grab the whole framebuffer of the wall VNC server (127.0.0.1:PORT) as a PNG.

rfbshot.py OUT.png [--vnc 5900] [--crop X,Y,W,H]
"""
import argparse
import socket
import struct
import sys
import zlib


def recvn(sock, n):
    data = bytearray()
    while len(data) < n:
        chunk = sock.recv(min(1 << 20, n - len(data)))
        if not chunk:
            raise RuntimeError('closed')
        data += chunk
    return bytes(data)


def png(path, w, h, rgb):
    raw = b''.join(b'\x00' + rgb[y * w * 3:(y + 1) * w * 3] for y in range(h))
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--vnc', type=int, default=5900)
    ap.add_argument('--crop')
    a = ap.parse_args()
    s = socket.create_connection(('127.0.0.1', a.vnc), timeout=20)
    recvn(s, 12)
    s.sendall(b'RFB 003.008\n')
    n = recvn(s, 1)[0]
    recvn(s, n)
    s.sendall(bytes([1]))
    assert struct.unpack('>I', recvn(s, 4))[0] == 0
    s.sendall(bytes([1]))
    w, h = struct.unpack('>HH', recvn(s, 4))
    recvn(s, 16)
    recvn(s, struct.unpack('>I', recvn(s, 4))[0])
    # 32 bpp, little endian, true colour, red at 16, green at 8, blue at 0.
    s.sendall(struct.pack('>BxxxBBBBHHHBBBxxx', 0, 32, 24, 0, 1, 255, 255, 255, 16, 8, 0))
    s.sendall(struct.pack('>BxHi', 2, 1, 0))  # Raw only
    s.sendall(struct.pack('>BBHHHH', 3, 0, 0, 0, w, h))
    fb = bytearray(w * h * 4)
    got = 0
    while got < w * h:
        t = recvn(s, 1)[0]
        if t == 0:
            recvn(s, 1)
            count = struct.unpack('>H', recvn(s, 2))[0]
            for _ in range(count):
                x, y, rw, rh, enc = struct.unpack('>HHHHi', recvn(s, 12))
                if enc != 0:
                    raise RuntimeError(f'encoding {enc}')
                data = recvn(s, rw * rh * 4)
                for row in range(rh):
                    start = ((y + row) * w + x) * 4
                    fb[start:start + rw * 4] = data[row * rw * 4:(row + 1) * rw * 4]
                got += rw * rh
        elif t == 2:
            pass
        elif t == 3:
            recvn(s, 3)
            recvn(s, struct.unpack('>I', recvn(s, 4))[0])
        elif t == 1:
            recvn(s, 1)
            first, count = struct.unpack('>HH', recvn(s, 4))
            recvn(s, count * 6)
        else:
            raise RuntimeError(f'message {t}')
    x0, y0, cw, ch = (0, 0, w, h)
    if a.crop:
        x0, y0, cw, ch = [int(v) for v in a.crop.split(',')]
    rgb = bytearray(cw * ch * 3)
    for yy in range(ch):
        for xx in range(cw):
            i = ((y0 + yy) * w + x0 + xx) * 4
            j = (yy * cw + xx) * 3
            rgb[j] = fb[i + 2]
            rgb[j + 1] = fb[i + 1]
            rgb[j + 2] = fb[i]
    png(a.out, cw, ch, bytes(rgb))
    print(f'{w}x{h} -> {a.out} {cw}x{ch}')


if __name__ == '__main__':
    sys.exit(main())
