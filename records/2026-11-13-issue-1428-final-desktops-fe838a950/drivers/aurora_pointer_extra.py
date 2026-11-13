from pathlib import Path
import time,re,json

def extra(r):
 base=Path(r.args.fixture[-1]).parent
 (base/'mode').write_text('qr');time.sleep(.5)
 previous=r.args.expect;r.args.expect=re.escape('https://example.test/acceptance/1428')
 try:r.receipt['correctedQrPassed']=r.trigger('qr-region-corrected',lambda:r.input.chord(r.args.keys))
 finally:r.args.expect=previous;(base/'mode').write_text('text')
 time.sleep(.5);r.input.click(960,540);time.sleep(.3);r.copy_sentinel('window-source-sentinel')
 start=r.cli('text.recognize',{'source':'window','copy':False});op=start['result']['operationId']
 data=r.wait(lambda:(lambda x:x if x.get('state') in ('completed','failed') else None)(r.cli('text.inspect',{'id':op})['result']),'external window source')
 r.receipt['correctedWindowSource']={'record':data,'paste':r.paste()};print(json.dumps({'correctedWindowSource':r.receipt['correctedWindowSource']}),flush=True)
