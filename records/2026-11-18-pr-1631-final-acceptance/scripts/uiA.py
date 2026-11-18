import sys,json,subprocess;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
O=os.path.expanduser('~/work/qr1618/state/out/')
opid,ins=edit_open('desktop'); save(opid,O+'rA-ui-orig.png'); open(O+'current-op','w').write(opid)
print(opid)
