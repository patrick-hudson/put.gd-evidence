from pathlib import Path
from PIL import Image
import json
E=Path.home()/'work/i1363/work/acceptance-1363/ap6'
a=Image.open(E/'shortcuts-bound-correct.png').crop((240,120,1020,744));a.save(E/'shortcuts-crop.png')
json.dump([{'kind':'rectangle','rect':[14,194,750,52]},{'kind':'rectangle','rect':[14,298,750,52]}],open(E/'shortcuts-spec.json','w'))
canvas=Image.new('RGB',(780,590),'#f4f4f2');canvas.paste(Image.open(E/'tray-menu.png').crop((898,207,1155,746)),(15,40));canvas.paste(Image.open(E/'tray-countdown.png').crop((505,0,775,65)),(325,100));canvas.save(E/'tray-compose.png')
json.dump([{'kind':'text','at':[15,10],'text':'Plasma Wayland - build 4498','fontPixels':20},{'kind':'rectangle','rect':[20,212,247,54]},{'kind':'text','at':[315,60],'text':'Tray started a 3 second capture','fontPixels':19},{'kind':'arrow','from':[430,205],'to':[440,135]},{'kind':'text','at':[310,240],'text':'Countdown visible; saved image clean','fontPixels':18}],open(E/'tray-spec.json','w'))
