import pass2 as p,fix6 as f,sys,json,subprocess
h=sys.argv[1]
for gap,count in [(.001,4 if h in ['f44','d69'] else 0),(.05,2 if h in ['f44','d69'] else 0)]:
 for i in range(count):
  f.with_fixture('cancel-extra',['python3',str(p.P/'qt_fixture.py'),'--rows','600'],lambda:f.cancel_case('cancel-extra-'+str(gap)+'-'+str(i),gap))
if h=='f44':
 c=subprocess.run(['sudo','-n','coredumpctl','--no-pager','list','gnome-shell','--since','2026-11-12 14:30:00 UTC'],capture_output=True,text=True);(p.P/'gnome-core-check.txt').write_text(c.stdout+c.stderr)
