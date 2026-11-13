from extra_main import extra as basic
from history_qr import extra as history

def extra(r):
 basic(r)
 try:history(r)
 except Exception as e:
  r.receipt['historyQrError']=str(e)
  print('HISTORY-QR-ERROR '+str(e),flush=True)
