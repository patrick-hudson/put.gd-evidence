from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import http.client,json,time,sys
root=Path(sys.argv[1]);root.mkdir(mode=0o700,exist_ok=True)
def mode():
 try:return json.loads((root/'control.json').read_text())
 except (OSError,ValueError):return {}
class H(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  data=self.rfile.read(int(self.headers.get('Content-Length','0')))
  if self.path=='/refuse' or mode().get('fail'):
   code=503;body=b'{"message":"Synthetic acceptance refusal"}'
  else:
   upstream=http.client.HTTPConnection('192.168.68.72',18361,timeout=30)
   headers={k:v for k,v in self.headers.items() if k.lower() not in ('host','connection')}
   headers.update(json.loads((root/'upstream.sxcu').read_text()).get('Headers',{}))
   upstream.request('POST','/api/upload',data,headers);reply=upstream.getresponse();code=reply.status;body=reply.read();upstream.close()
  with (root/'events.jsonl').open('a') as f:f.write(json.dumps({'status':code,'bytes':len(data),'held':bool(mode().get('hold'))})+'\n')
  deadline=time.monotonic()+180
  while code<400 and mode().get('hold') and time.monotonic()<deadline:time.sleep(.2)
  self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers()
  try:self.wfile.write(body)
  except (BrokenPipeError,ConnectionResetError):pass
ThreadingHTTPServer(('192.168.68.72',18432),H).serve_forever()
