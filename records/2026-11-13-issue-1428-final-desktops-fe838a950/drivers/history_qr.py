import http.server,threading,json,time,subprocess
from pathlib import Path
URL='https://example.test/acceptance/1428/image.png'
def extra(r):
 out=r.receipt['historyQr']={}
 class Handler(http.server.BaseHTTPRequestHandler):
  def do_POST(self):
   self.rfile.read(int(self.headers.get('Content-Length','0')));body=json.dumps({'url':URL}).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  def log_message(self,*args):pass
 server=http.server.HTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  sx=r.root/'local.sxcu';sx.write_text(json.dumps({'Version':'17.0.0','Name':'Isolated synthetic receiver','DestinationType':'ImageUploader, FileUploader','RequestMethod':'POST','RequestURL':f'http://127.0.0.1:{server.server_port}/upload','Body':'MultipartFormData','FileFormName':'file','URL':'{json:url}'}))
  rev=r.cli('settings.get')['result']['metadata']['acceptedRevision']
  out['import']=r.cli('settings.importUploader',{'path':str(sx),'expectedRevision':rev,'credentialMode':'session','profileId':'qr-lab'})
  archive=r.root/'archive';archive.mkdir(exist_ok=True);rev=r.cli('settings.get')['result']['metadata']['acceptedRevision']
  r.cli('settings.patch',{'patch':{'archive':{'keepUploads':True,'root':str(archive)}},'expectedRevision':rev})
  p=Path(r.args.fixture[-1]).parent/'text.png'
  op=r.cli('upload.files',{'paths':[str(p)],'profileId':'qr-lab'})['result']['operationId']
  state=r.wait(lambda:(lambda x:x if x.get('state') in ('completed','failed') else None)(r.cli('operation.inspect',{'id':op})['result']),'synthetic upload end',30);out['upload']=state
  ident=state['items'][0]['artifact']['id'];out['historyId']=ident
  r.copy_sentinel('history-text-sentinel');t=r.cli('history.copyText',{'id':ident,'keepResult':True})['result']['operationId'];out['text']=r.wait(lambda:(lambda x:x if x.get('state') in ('completed','failed') else None)(r.cli('text.inspect',{'id':t})['result']),'history text end');out['paste']=r.paste()
  r.cli('ui.show',{'view':'history'});time.sleep(1);r.input.chord(['alt','tab']);time.sleep(1)
  out['show']=r.cli('history.qr',{'id':ident,'mode':'show'});time.sleep(1)
  if r.args.rfb!='none':subprocess.run(['python3',r.args.rfb,str(r.args.rfb_port),str(r.root/'history-qr-dialog.png')],check=True)
  out['saved']=r.cli('history.qr',{'id':ident,'mode':'save','path':str(r.root/'history-qr.png')});out['expected']=URL
  r.input.chord(['esc'])
 finally:server.shutdown();server.server_close()
 print(json.dumps({'historyQr':out}),flush=True)
