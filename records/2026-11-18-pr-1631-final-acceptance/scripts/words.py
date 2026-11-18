import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
opid,ins=edit_open('desktop')
res('editor.recognize',{'id':opid})
for _ in range(60):
    t=inspect(opid)['text']
    if t['state']=='completed': break
    time.sleep(1)
for w in t['words']:
    if True: print(w['rect'],repr(w['text']),w['confidence'])
cancel(opid)
