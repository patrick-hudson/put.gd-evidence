from pathlib import Path
import sys,json
sys.path.insert(0,str(Path.home()/'work/b1428/r'))
from tools.lab.desktop_lock import Desktop
D=Desktop(Path.home()/'putgd-lab/locks','k72');original=D.inventory;foreign=[]
def inventory():
 items,notes=original();foreign.clear()
 for x in items:
  # This worker never launched anything from the engine worker's checkout.
  # Scope the exception to exact identities in the actual cleanup snapshot.
  if x['kind']=='process' and x['detail'].split(' ',1)[0] in ('/home/patrick/work/text-engine/src/build/dev/putgd-ocr',):foreign.append(x['key'])
 return items,notes
D.inventory=inventory
print(json.dumps(D.release('b1428-8a-k72',verified_clean=True,not_mine=lambda:foreign),indent=2))
