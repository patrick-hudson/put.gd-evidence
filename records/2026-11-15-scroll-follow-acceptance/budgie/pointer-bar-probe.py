import accept as A,time,json,re,rfb
from pathlib import Path
P=A.P;sid=None
try:
 assert not A.remote('helper-pids')
 A.L.browser_start('firefox');b,_=A.L.connect();b.navigate('https://en.wikipedia.org/wiki/Linux');time.sleep(6)
 A.remote('flat');A.remote('anchor','960','540');offset=(P/'helper.log').stat().st_size
 sid=A.rpc('scroll.prepare',{'rect':[240,200,1440,820],'driver':'user'})['id'];A.rpc('scroll.start',{'id':sid});time.sleep(1)
 s=rfb.RFB(5941);s.screenshot(P/'pointer-bar-calibration.png');s.close()
 text=(P/'helper.log').read_bytes()[offset:].decode();lines=[l for l in text.splitlines()if 'scroll: bar at'in l];assert lines
 proof={'operationId':sid,'inspect':A.rpc('scroll.inspect',{'id':sid}),'helperBarLines':lines,'source':'Real native QEMU framebuffer before pointer benchmark. No mouse movement after prepare.'};(P/'pointer-bar-calibration.json').write_text(json.dumps(proof,indent=1));print(json.dumps(proof),flush=True)
finally:
 if sid:
  try:A.rpc('scroll.cancel',{'id':sid})
  except Exception:pass
 A.L.browser_stop()
