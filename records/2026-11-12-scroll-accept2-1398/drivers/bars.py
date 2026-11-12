import pass2 as p,fix6 as f,json,subprocess,time
P=p.P
while not (P/'file-manager.done').exists():time.sleep(2)
if __import__('sys').argv[1]=='d69':
 while not (P/'file-manager2.done').exists():time.sleep(2)
subprocess.run(['python3',str(P/'restart-resident.py')],check=True)
for n in ['classicforced','overlayforced']:
 for i in range(2):f.with_fixture(n,['firefox','--no-remote','--profile',str(P/'ffprofile'),'--kiosk',(P/(n+'.html')).as_uri()],lambda:p.capture('firefox-probe-'+n+'-'+str(i),60,40000),18)
(P/'bars.done').write_text('done')
