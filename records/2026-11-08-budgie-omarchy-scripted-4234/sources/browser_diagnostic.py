import sys,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab
run=Path(sys.argv[1]).resolve();target='/dev/shm/sp-browser-diagnostic.py'
lab.put(run,'tools/lab/surface_driver/browser.py',target)
code=r'''import importlib.util,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('br','/dev/shm/sp-browser-diagnostic.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
paths=list(Path('/dev/shm/sp-firefox').rglob('transaction.json'));assert len(paths)==1
state=json.loads(paths[0].read_text());c=b._Marionette(state['port']);out=[]
for h in c.call('WebDriver:GetWindowHandles'):
 c.call('WebDriver:SwitchToWindow',{'handle':h,'focus':False})
 out.append(c.script("""const t=document.body?.innerText||'';return {blank:location.href==='about:blank',protonHost:/(^|\\.)proton\\.(me|ch)$/.test(location.hostname),hasFragment:location.hash.length>1,focused:document.hasFocus(),visible:document.visibilityState==='visible',titleProton:/Proton/i.test(document.title),media:document.querySelectorAll('img,video,canvas').length,expired:/expired|unavailable|not found|could not/i.test(t),password:/password/i.test(t),browserUnsupported:/browser.*support|support.*browser/i.test(t),download:/Download/i.test(t),bodyPresent:t.length>100};"""))
c.close();print(json.dumps(out));Path('/dev/shm/sp-browser-diagnostic.py').unlink()
'''
raw=lab.guest_session(run,"python3 - <<'DIAG'\n"+code+'\nDIAG\n');print(raw)
