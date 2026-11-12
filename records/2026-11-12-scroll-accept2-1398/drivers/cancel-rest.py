from pathlib import Path
import sys,traceback
source=Path('/home/patrick/work/sa2/review-extra.py').read_text();exec(source.split('try:\n for i in range(2)')[0],globals())
failures=[]
def run():
 for phase in ['start','stop']:
  for i in range(3 if h in ['f44','d69'] else 1):
   if (P/('cancel-'+phase+'-'+str(i))).exists():continue
   try:cancel(phase,i)
   except Exception:failures.append(traceback.format_exc())
fixture(['--rows','600'],run)
if not (P/'after-cancels').exists():fixture(['--rows','60'],lambda:p.capture('after-cancels',60,40000))
(P/'cancel-rest-errors.json').write_text(json.dumps(failures,indent=2));(P/'extra.done').write_text('done; see failed cancel outcomes')
