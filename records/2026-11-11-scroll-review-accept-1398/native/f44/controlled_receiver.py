from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
import json,hashlib,time
p=Path('/home/patrick/work/sr8/received');p.mkdir(exist_ok=True)
class H(BaseHTTPRequestHandler):
 def do_POST(self):
  b=self.rfile.read(int(self.headers['Content-Length']));name=str(time.time_ns());(p/(name+'.bin')).write_bytes(b)
  with open(p/'receipts.jsonl','a') as f:f.write(json.dumps({'id':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})+'\n')
  
  while (p.parent/'hold-upload').exists():time.sleep(.02)
  status=500 if (p.parent/'fail-upload').exists() else 200
  data=json.dumps({'url':'http://127.0.0.1:19399/'+name}).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_GET(self):
  self.send_response(200);self.end_headers();self.wfile.write(b'synthetic acceptance upload')
HTTPServer(('127.0.0.1',19399),H).serve_forever()
