import pass2 as p,fix6 as f,subprocess,time,json,traceback
P=p.P
while not (P/'extra.done').exists():time.sleep(2)
for name in ['sticky','sidebar','classic','overlay','blank','hover','shrink']:
 for i in range(2):
  try:
   ff=P/'ffprofile'
   def run():
    r=p.capture('firefox-probe-'+name+'-'+str(i),60,40000,header=40 if name=='sticky' else 0,footer=40 if name=='sticky' else 0)
    if name in ['sidebar','blank','shrink']:
     # The ordinary ruler oracle is inapplicable; preserve its raw mismatch and leave independent adjudication pending.
     (P/('firefox-probe-'+name+'-'+str(i))/'ORACLE-PENDING').write_text('Requires variant-specific oracle. Raw ruler result is not an acceptance verdict.')
   f.with_fixture(name,['firefox','--no-remote','--profile',str(ff),'--kiosk',(P/(name+'.html')).as_uri()],run,18)
  except Exception:(P/(name+'-'+str(i)+'.error')).write_text(traceback.format_exc())
(P/'probes.done').write_text('done')
