import accept as A,json,time,base64,io
from pathlib import Path
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
P=A.P;L=A.L;D=P/'runs/chromium-github-user-Cchrome-1';profile=P/'profile-chromium'
if profile.exists():profile.rename(P/(profile.name+'-before-reference-'+str(time.time_ns())))
try:
 L.browser_start('chromium');b,_=L.connect();b.navigate('https://github.com/patrick-hudson/put.gd-desktop/pull/1398');time.sleep(8);before=L.wait_loaded(b,25);assert before['clientWidth']==1905,before
 b.js('window.scrollTo({top:0,behavior:"instant"});return 0;');time.sleep(2)
 # Same CDP tiles, but clip to the measured layout width, excluding the scrollbar.
 h=before['docHeight'];w=before['clientWidth'];out=Image.new('RGB',(w,h),'white')
 for y in range(0,h,4000):
  hh=min(4000,h-y);obj=b.cmd('Page.captureScreenshot',{'format':'png','captureBeyondViewport':True,'clip':{'x':0,'y':y,'width':w,'height':hh,'scale':1}});out.paste(Image.open(io.BytesIO(base64.b64decode(obj['data']))).convert('RGB'),(0,y))
 out.save(D/'reference-clientwidth-original.png');out.crop((0,6,w,h-2)).save(D/'reference-clientwidth.png');after=b.js(L.INFO)
 b.js('window.scrollTo({top:18000,behavior:"instant"});return 0;');time.sleep(1);obj=b.cmd('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False});(D/'reference-live-viewport.png').write_bytes(base64.b64decode(obj['data']))
 (D/'reference-recheck.json').write_text(json.dumps({'before':before,'after':after,'clipWidth':w,'fullBrowserWidth':before['w'],'originalRunDocumentHeight':json.loads((D/'result.json').read_text())['before']['docHeight'],'liveViewportAt':b.js(L.INFO),'productCaptured':False},indent=1));print('REFERENCE COLLECTED',before['docHeight'],w,flush=True)
finally:L.browser_stop()
