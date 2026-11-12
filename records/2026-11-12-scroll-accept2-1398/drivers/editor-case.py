import pass2 as p,fix6 as f,time,json,numpy as np
from PIL import Image
P=p.P
while not (P/'controls.done').exists():time.sleep(2)
# MCP owns the next slot; this case runs only after its verifier has saved the result.
while not (P/'mcp/result.json').exists():time.sleep(2)
for i in range(2):
 r=f.with_fixture('editor', ['python3',str(P/'editor_fixture.py'),'--rows','600','--start','23400'],lambda:p.capture('editor-'+str(i),600,40000))
 d=P/('editor-'+str(i));png=d/'capture.png'
 if png.exists():
  im=np.asarray(Image.open(png).convert('RGB')).astype('int16');h,w,_=im.shape;y=np.arange(h);expected=np.stack([30+(y*17)%190,40+(y*23)%180,50+(y*31)%170],axis=1);bad=int(np.count_nonzero(np.any(im[:,860:]-expected[:,None,:],axis=2)))
  (d/'minimap-prefix-verification.json').write_text(json.dumps({'oracle':'minimap top layout extended at one screen pixel per row; rate changes at scroll / 3','height':h,'minimapMismatchPixels':bad,'exactPrefix':bad==0},indent=2))
(P/'editor.done').write_text('done')
