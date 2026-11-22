"""Send one command to driver.py: dc.py SOCKET '["method", args...]'"""
import socket, sys
s = socket.socket(socket.AF_UNIX); s.connect(sys.argv[1]); s.settimeout(900)
s.sendall(sys.argv[2].encode() + b'\n')
data = b''
while not data.endswith(b'\n'):
    chunk = s.recv(65536)
    if not chunk: break
    data += chunk
sys.stdout.write(data.decode())
