from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
Image.MAX_IMAGE_PIXELS=None
P=Path.cwd();prior=Image.open(Path.home()/'work/sfr17/runs/firefox-github-user-A1-3/capture.png').convert('RGB')
boxes={'A-1':[976,1932,1207,1981],'A-2':[976,442,1168,473],'A-5':[936,695,1196,738],'A-6':[936,1104,1207,1163],'A-8':[936,1794,1207,1850]};summary=[]
for tag,box in boxes.items():
 d=P/'runs'/('firefox-github-user-'+tag);r=json.loads((d/'result.json').read_text());c=r['capture'];a=Image.open(d/'capture.png').convert('RGB');b=Image.open(d/'reference.png').convert('RGB');l,t,rr,bt=box;bounds=(l-20,t-20,rr+20,bt+20);tiles=[im.crop(bounds)for im in [a,b,prior]];pic=Image.new('RGB',(tiles[0].width*3+24,tiles[0].height+24),'white');draw=ImageDraw.Draw(pic)
 for i,(tile,label)in enumerate(zip(tiles,['current capture','current reference','prior f19043f6b capture'])):x=i*(tile.width+12);pic.paste(tile,(x,24));draw.text((x,0),label,fill='red')
 pic.save(d/'cutout-comparison.png');ar=np.asarray(a.crop(box));br=np.asarray(b.crop(box));pr=np.asarray(prior.crop(box));mask=(ar.min(2)>248)&(br.min(2)<220)
 row=dict(run=d.name,page='GitHub PR1398',browser='Firefox',mode='you scroll',desktop='m74 Cinnamon X11',box=box,rowsInclusive=[t,bt-1],width=rr-l,height=bt-t,boundingAreaPixels=(rr-l)*(bt-t),whiteMissingInkPixels=int(mask.sum()),priorWhiteAtSameMissingPixels=int(((pr.min(2)>248)&mask).sum()),hiddenCells=c.get('hiddenCells',c['result'].get('hiddenCells')),hiddenRows=c.get('hiddenRows',c['result'].get('hiddenRows')),unwritten=(d/'unwritten.log').read_text().strip(),note=c.get('note'),foundAgain=c.get('foundAgain'),comparison='cutout-comparison.png',priorObservation='Corresponding area is intact in the one retained prior image; this alone does not prove a regression.')
 (d/'cutout.json').write_text(json.dumps(row,indent=1));summary.append(row)
(P/'cutout-summary.json').write_text(json.dumps(summary,indent=1))
d=P/'runs/firefox-github-user-Afast-2';a=np.asarray(Image.open(d/'capture.png').convert('RGB'));b=np.asarray(Image.open(d/'reference.png').convert('RGB'));detail=dict(run=d.name,page='GitHub PR1398',browser='Firefox',mode='you scroll, faster pace',desktop='m74 Cinnamon X11',rowsInclusive=[9913,10480],rowCount=568,lastPlacedFrame=[9560,10480],classification='DAMAGED',whitePixelsWritten=True,unwrittenTailCells=int((a[9913:].max(2)==0).sum()),pagePositionGapObserved=False,location='Image tail, within extent of last placed frame before loss',cause='Written white pixels replace reference table content. No raw frame dump exists to establish whether the browser supplied unpainted pixels; no page-position gap is shown.',lossTimes={'lastPlaced':'22:46:05.571 t=673797 position9560','firstSkipped':'22:46:05.586 t=673821','lost':'22:46:05.671 t=673864'})
(d/'damaged.json').write_text(json.dumps(detail,indent=1))
print(json.dumps(summary,indent=1))
