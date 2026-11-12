from pathlib import Path
from http.server import HTTPServer,BaseHTTPRequestHandler
import hashlib,json,struct,time
P=Path('/tmp/cp2')
class H(BaseHTTPRequestHandler):
 def do_POST(self):
  b=self.rfile.read(int(self.headers['Content-Length']));(P/'received.multipart').write_bytes(b);i=b.index(b'\x89PNG\r\n\x1a\n');j=i+8
  while True:
   n=struct.unpack('>I',b[j:j+4])[0];kind=b[j+4:j+8];j+=n+12
   if kind==b'IEND':break
  png=b[i:j];(P/'received.png').write_bytes(png);(P/'receiver-receipt.json').write_text(json.dumps({'multipartSha256':hashlib.sha256(b).hexdigest(),'pngSha256':hashlib.sha256(png).hexdigest(),'pngBytes':len(png),'multipartBytes':len(b)},indent=2))
  while (P/'hold-upload').exists():time.sleep(.02)
  data=b'{"url":"http://127.0.0.1:19511/fixture"}';self.send_response(200);self.send_header('Content-Length',str(len(data)));self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data)
HTTPServer(('127.0.0.1',19511),H).serve_forever()
