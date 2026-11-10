from PIL import Image
from pathlib import Path
import json
E=Path('/home/patrick/work/i1363/work/acceptance-1363/ab9')
Image.open(E/'shortcuts-bound.png').crop((240,120,985,680)).save(E/'shortcuts-crop.png')
Image.open(E/'tray-delay3-countdown.png').crop((375,0,650,115)).save(E/'countdown-crop.png')
(E/'shortcuts-shapes.json').write_text(json.dumps([dict(kind='rectangle',rect=[9,190,724,58]),dict(kind='rectangle',rect=[9,294,724,58]),dict(kind='text',at=[20,56],text='Budgie labwc bridge: both bindings confirmed',fontPixels=19)]))
(E/'countdown-shapes.json').write_text(json.dumps([dict(kind='rectangle',rect=[20,12,236,36],width=3),dict(kind='text',at=[12,72],text='Budgie tray: 3-second capture',fontPixels=17)]))
