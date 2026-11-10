import subprocess,os,time,sys,json,gi
from pathlib import Path
import numpy as np
from PIL import Image
gi.require_version('Gst','1.0');from gi.repository import Gst
Gst.init(None); out=Path(os.environ['OUT']);out.mkdir(parents=True,exist_ok=True)
p=subprocess.Popen([str(Path(__file__).parent/'kwin'),os.environ.get('SCALE','1')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
node=p.stdout.readline().strip();print('node',node,flush=True)
pipe=Gst.parse_launch(f'pipewiresrc path={node} ! queue leaky=downstream max-size-buffers=2 ! videoconvert ! video/x-raw,format=RGB ! appsink name=tap max-buffers=2 drop=true sync=false');tap=pipe.get_by_name('tap');pipe.set_state(Gst.State.PLAYING)
def frame(name):
 time.sleep(2)
 for i in range(2):sample=tap.emit('try-pull-sample',3*Gst.SECOND)
 if sample is None:raise RuntimeError('no frame')
 caps=sample.get_caps().get_structure(0);w=caps.get_value('width');h=caps.get_value('height');buf=sample.get_buffer();ok,m=buf.map(Gst.MapFlags.READ);a=np.frombuffer(m.data,dtype=np.uint8).reshape(h,-1)[:,:w*3].reshape(h,w,3).copy();buf.unmap(m);Image.fromarray(a).save(out/(name+'.png'));print(json.dumps({'frame':name,'size':[w,h]}),flush=True)
try:
 frame('before');p.stdin.write('\n');p.stdin.flush();frame('after')
finally:
 pipe.set_state(Gst.State.NULL);p.stdin.write('\n');p.stdin.flush();p.wait(timeout=5)
