import fix6 as f,pass2 as p,json,shutil,hashlib
import numpy as np
from PIL import Image
settings=p.rpc('settings.get');p.rpc('settings.patch',{'patch':{'preferences':{'scrollCaptureFromTop':True,'notifications':False}},'expectedRevision':settings['metadata']['observedRevision']})
for i in range(2):
 name='new-late-ruler-verified-'+str(i)
 r,o=f.with_fixture(name,['python3',str(p.P/'late_fixture.py'),'late'],lambda:f.cap(name,maxh=30000),ACCEPT3_RULER='1')
 for suffix in ['generator','top','footer']:
  source=p.P/('late-'+suffix+'.png')
  if source.exists():shutil.copyfile(source,o/('reference-'+suffix+'.png'))
 if (o/'capture.png').exists():
  im=np.asarray(Image.open(o/'capture.png').convert('RGB'));ref=np.asarray(Image.open(o/'reference-generator.png').convert('RGB'));h=len(im);footer=np.asarray(Image.open(o/'reference-footer.png').convert('RGB'));head=np.asarray(Image.open(o/'reference-top.png').convert('RGB')) if (o/'reference-top.png').exists() else None
  bodyh=max(0,h-36);a=np.any(im[:bodyh]!=ref[:bodyh],axis=2);b=np.any(im[-36:]!=footer,axis=2)
  r['oracle']={'height':h,'bodyRows':bodyh,'expectedBodyRows':24000,'bodyMismatchPixels':int(a.sum()),'footerMismatchPixels':int(b.sum()),'lateHeaderAtTop':bool(head is not None and np.array_equal(im[:36],head)),'allBodyRowsInOrder':bodyh==24000 and not bool(a.any()),'generatorSha256':hashlib.sha256((o/'reference-generator.png').read_bytes()).hexdigest()}
 f.save(r,o)
