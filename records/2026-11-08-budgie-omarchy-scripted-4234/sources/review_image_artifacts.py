"""Independent review of saved image pixels; no app/session state is trusted."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
checks=[]
for row in json.load(open('work/sp1275/progress.json')):
 run=row['run'];phase=Path(row['cells']['edit_upload']['attempt']).parent.name;root=Path('work/sp1275/export')/run/'files/attempts'/phase
 original=Image.open(root/'source.png').convert('RGBA');actual=Image.open(root/'edited-upload.png').convert('RGBA');assert actual.size==original.size==(640,320)
 assert actual.getextrema()[3]==(255,255)
 assert set(actual.crop((355,25,585,135)).getdata())=={(0,0,0,255)}
 masked=actual.copy()
 for rect in ((20,20,265,105),(345,15,595,145)):masked.paste(original.crop(rect),rect)
 assert masked.tobytes()==original.tobytes(),(run,'changed outside requested marks')
 # RGBA difference has zero alpha even when RGB changes; use RGB for bbox.
 assert ImageChops.difference(actual.crop((20,20,265,105)).convert('RGB'),original.crop((20,20,265,105)).convert('RGB')).getbbox()
 checks.append(dict(run=run,opaque=True,dimensions=[640,320],solidRedactionInterior=True,arrowChangesPixels=True,unmarkedPixelsUnchanged=True,imageSha256=hashlib.file_digest((root/'edited-upload.png').open('rb'),'sha256').hexdigest()))
Path('work/sp1275/image-artifact-review.json').write_text(json.dumps(checks,indent=2));print('verified original pixels outside marks on all five rows')
