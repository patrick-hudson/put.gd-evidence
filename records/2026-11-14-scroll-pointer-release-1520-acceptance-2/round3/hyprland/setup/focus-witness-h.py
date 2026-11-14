from pathlib import Path
import json,subprocess,time,sys,os,shutil
l=Path.home()/'work/s5302';a=l/'a';phase=sys.argv[1]
def ctl(*args):return subprocess.check_output(['hyprctl',*args],text=True)
cs=json.loads(ctl('clients','-j'));term=next(v for v in cs if v.get('class')=='foot');browser=next(v for v in cs if v.get('class')=='chromium')
def dispatch(name,fields,win):
 code='hl.dispatch(hl.dsp.'+name+'({'+(fields+',' if fields else '')+'window=hl.get_window('+json.dumps('address:'+win['address'])+')}))'
 return ctl('eval',code)
dispatch('focus','',browser)
if browser.get('fullscreen'):dispatch('window.fullscreen','mode="fullscreen",action="unset"',browser)
dispatch('window.float','action="on"',term);dispatch('window.resize','x=850,y=450,relative=false',term);dispatch('window.move','x=550,y=320,relative=false',term);dispatch('focus','',browser);time.sleep(.2)
(a/(phase+'-layers-paused.json')).write_text(ctl('layers','-j'));(a/(phase+'-focus-before.json')).write_text(ctl('activewindow','-j'))
subprocess.run(['python3',str(l/'input-click-h.py'),'900','500'],check=True)
v=json.loads(ctl('activewindow','-j'));(a/(phase+'-focus-after.json')).write_text(json.dumps(v,indent=2));assert v.get('pid')==term['pid'],v
subprocess.run(['sudo','-n','python3',str(l/'keyboard.py')],check=True);time.sleep(.4)
s=(a/'terminal-received.txt').read_text();assert s=='abc\n',s
shutil.copyfile(a/'terminal-received.txt',a/(phase+'-received.txt'));offset=int((a/'terminal-offset.txt').read_text());lines=(a/'helper.log').read_bytes()[offset:].decode().splitlines();injected=[x for x in lines if 'scroll inject:' in x];(a/(phase+'-quiet.json')).write_text(json.dumps({'injectionLines':injected},indent=2));assert not injected,injected
for n in ['terminal-paused.json','terminal-session-id','terminal.pid']:
 shutil.copyfile(a/n,a/(phase+'-'+n))
print(json.dumps({'phase':phase,'windowPid':term['pid'],'witness':s,'injections':injected}),flush=True)
