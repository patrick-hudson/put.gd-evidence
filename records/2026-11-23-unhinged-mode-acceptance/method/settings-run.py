import json, subprocess as sp, sys
from pathlib import Path
p=Path(__file__).parent
h=sys.argv[1]
root=(p/f'{h}.root').read_text().strip()
def req(*parts):
    reply=sp.run([str(p/'call'),h,json.dumps(parts)],capture_output=True,text=True)
    result=json.loads(reply.stdout)
    if not result['ok']: raise RuntimeError(result['error'])
    return result['result']
def shot(action):
    box=req('settings')
    tsv=sp.check_output([str(p/'host'),h,'tesseract '+root+'/settings-probe.png stdout tsv 2>/dev/null'],text=True)
    for line in tsv.splitlines():
        fields=line.split('\t')
        if fields[-1].strip().lower()=='unhinged':
            x,y,w,height=map(int,fields[6:10])
            break
    else:
        raise RuntimeError('cannot find Unhinged mode in the cropped Settings window')
    if action=='on':
        status=req('setting')
        if not status['present']:
            req('shot','settings-A')
        elif status['value']:
            raise RuntimeError('expected Unhinged mode off before enabling')
        result=req('click',box[0]+x+w//2,box[1]+y+height//2,'B')
        if result['settings']['value']!=True or result['settings']['diskValue']!=True:
            raise RuntimeError('click did not persist true')
    else:
        result=req('click',box[0]+x+w//2,box[1]+y+height//2,'C')
        if result['settings']['value']:
            raise RuntimeError('click did not turn off Unhinged mode')
    print(json.dumps(result))
    req('key','close')
shot(sys.argv[2])
