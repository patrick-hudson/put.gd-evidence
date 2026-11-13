"""Synthetic-only offline receiver and HTTP profile for acceptance drivers."""
import importlib.util,json,pathlib,threading
from http.server import ThreadingHTTPServer

def configure(driver,build):
 path=pathlib.Path(__file__).parent/'tests/fixtures/http_uploader_server.py'
 spec=importlib.util.spec_from_file_location('sweep_http_fixture',path); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
 module.state['auth']='none'
 server=ThreadingHTTPServer(('127.0.0.1',0),module.Handler); server.daemon_threads=True
 threading.Thread(target=server.serve_forever,daemon=True).start()
 origin='http://127.0.0.1:'+str(server.server_address[1])
 uploader={'Version':'17.0.0','Name':'Sweep offline acceptance','DestinationType':'FileUploader','RequestMethod':'POST','RequestURL':origin+'/upload/json','Body':'MultipartFormData','FileFormName':'file','URL':'{json:files[0].url}','DeletionURL':'{json:files[0].delete}'}
 p=driver.run/'offline.sxcu'; p.write_text(json.dumps(uploader))
 settings=driver.cli(build,'settings.get')
 v=driver.cli(build,'settings.importUploader',{'path':str(p),'profileId':'sweep-http','label':'Sweep offline acceptance','credentialMode':'session','allowInsecureHttp':True,'expectedRevision':settings['metadata']['observedRevision']})
 settings=driver.cli(build,'settings.get')
 driver.cli(build,'settings.patch',{'patch':{'actions':{name:{'destination':'upload','profileId':v['profileId']} for name in ('edit','region','record','clipboard')}},'expectedRevision':settings['metadata']['observedRevision']})
 return server,module,origin
