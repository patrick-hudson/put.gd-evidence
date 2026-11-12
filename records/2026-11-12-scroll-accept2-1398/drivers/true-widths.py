import pass2 as p,fix6 as f,time,os,sys
P=p.P
while not (P/'editor.done').exists():time.sleep(2)
if sys.argv[1]=='m74':
 while not (P/'fallback-proxy2.done').exists() and not (P/'fallback-proxy2.error').exists():time.sleep(2)
for width,num in [(600,2),(1280,1)]:
 os.environ['SC_TEXT_WIDTH']=str(width)
 for i in range(num):f.with_fixture('true-qt-width', ['python3',str(P/'native_text_fixture.py'),'qt',str(width),'bottom'],lambda:p.capture('qt-true-'+str(width)+'-'+str(i),60,60000,text=True))
(P/'widths.done').write_text('done')
