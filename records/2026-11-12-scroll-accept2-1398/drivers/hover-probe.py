import pass2 as p,fix6 as f,time
P=p.P
while not (P/'bars.done').exists():time.sleep(2)
for i in range(2):f.with_fixture('hoverforced',['firefox','--no-remote','--profile',str(P/'ffprofile'),'--kiosk',(P/'hoverforced.html').as_uri()],lambda:p.capture('firefox-probe-hoverforced-'+str(i),60,40000),18)
(P/'hover.done').write_text('done')
