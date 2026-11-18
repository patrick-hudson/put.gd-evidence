import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
opid,ins=edit_open('desktop')
O=os.path.expanduser('~/work/qr1618/state/out/')
save(opid,O+sys.argv[1]+'-orig.png')
print(opid)
open(O+'current-op','w').write(opid)
