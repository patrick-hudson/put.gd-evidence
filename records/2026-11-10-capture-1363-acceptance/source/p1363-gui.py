import sys,json,time
from pathlib import Path
exec(compile(Path('/tmp/p1363-checks.py').read_text().split('build = cli(')[0],'/tmp/p1363-checks.py','exec'))
E=Path(ROOT)/'work/acceptance-1363'/run;E.mkdir(parents=True,exist_ok=True)
with (E/'temporary-work-dirs.jsonl').open('a') as index:index.write(json.dumps({'path':WORK,'run':run,'mode':sys.argv[4]})+'\n')
def save(n,d):(E/(n+'.json')).write_text(json.dumps(d,indent=2));return d
def photo(n,head=0):dump(head).save(E/(n+'.png'))
def key(*keys):return lab('key','--run',RUN,*keys)
def keyop(keys,name):
 before={v['id'] for v in cli('operation.recent')['operations']};began=time.monotonic();key(*keys)
 for _ in range(80):
  rows=[v for v in cli('operation.recent')['operations'] if v['id'] not in before]
  if rows:break
  time.sleep(.1)
 assert len(rows)==1,rows
 r=wait(rows[0]['id']);save(name,cli('operation.inspect',{'id':rows[0]['id']}));r['elapsed']=time.monotonic()-began;return r
mode=sys.argv[4]
if mode=='bind-cinnamon':
 click(1256,28);time.sleep(1);click(85,218);time.sleep(1);photo('shortcuts-before-binding')
 click(900,286);time.sleep(1);key('ctrl','alt','r');time.sleep(2)
 click(900,443);time.sleep(1);key('ctrl','alt','m');time.sleep(3);photo('shortcuts-bound')
 doc=save('bound-settings',cli('settings.get'));assert doc['document']['actions']['repeat']['shortcut']=='Ctrl+Alt+R',doc['document']['actions'];assert doc['document']['actions']['monitor']['shortcut']=='Ctrl+Alt+M',doc['document']['actions']
 save('bound-capabilities',cli('capabilities'))
 r=keyop(('ctrl','alt','r'),'key-repeat-empty');time.sleep(.7);photo('key-repeat-empty');assert r['code']=='repeat_unavailable',r
 move(1680,400);r=keyop(('ctrl','alt','m'),'key-monitor-head1');im=fetch(r['path']);im.save(E/'key-monitor-head1.png');assert im.size==(1024,768),im.size
 print('GUI bindings, refusal, real monitor key on head1 passed',flush=True)
elif mode=='photo':photo(sys.argv[5],int(sys.argv[6]) if len(sys.argv)>6 else 0)
elif mode=='click':click(int(sys.argv[5]),int(sys.argv[6]));time.sleep(1);photo(sys.argv[7],int(sys.argv[8]) if len(sys.argv)>8 else 0)
elif mode=='move':move(int(sys.argv[5]),int(sys.argv[6]));time.sleep(1);photo(sys.argv[7],int(sys.argv[8]) if len(sys.argv)>8 else 0)
elif mode=='right':
 x,y=int(sys.argv[5]),int(sys.argv[6])
 if desktop in ('budgie','hyprland'):guest(ENV+'python3 /tmp/wayland_pointer.py click %d %d --button right --extent %d %d' % (x,y,*EXTENT))
 else:
  head=locate(x,y)[0] if desktop=='cinnamon' else None;move(x,y);qmp([{'type':'btn','data':{'down':True,'button':'right'}}],head);time.sleep(.15);qmp([{'type':'btn','data':{'down':False,'button':'right'}}],head)
 time.sleep(1);photo(sys.argv[7],int(sys.argv[8]) if len(sys.argv)>8 else 0)
elif mode=='key':key(*sys.argv[5:]);time.sleep(.8)
elif mode=='native-region':
 before={v['id'] for v in cli('operation.recent')['operations']};key('ctrl','shift','1');time.sleep(1);photo('plain-shortcut-selector');drag(300,300,600,500);released=time.monotonic()
 rows=[v for v in cli('operation.recent')['operations'] if v['id'] not in before];assert len(rows)==1;op=rows[0]['id'];r=wait(op);save('plain-shortcut-region',cli('operation.inspect',{'id':op}));im=fetch(r['path']);im.save(E/'plain-shortcut-region.png');assert im.size==(300,200);assert time.monotonic()-released<2.8
 move(700,600);r=keyop(('ctrl','alt','r'),'key-repeat');rep=fetch(r['path']);rep.save(E/'key-repeat.png');save('repeated-capabilities',cli('capabilities'));box=ImageChops.difference(im,rep).getbbox();corner=bool(desktop=='hyprland' and box and box[0]>=im.width-16 and box[1]>=im.height-16);save('key-repeat-pixels',{'differenceBox':box,'knownHyprlandCornerCursorObserved':corner,'samePixels':box is None});assert box is None or corner,box
 print('plain shortcut region immediate; key repeat identical' if not box else 'plain shortcut region/repeat rectangle passed; known Hyprland corner cursor observed in saved images',flush=True)
elif mode=='inspect':save('operations',cli('operation.recent'));save('settings-current',cli('settings.get'));save('diagnostics-current',cli('diagnostics'));save('capabilities-current',cli('capabilities'))
elif mode=='cli':print(json.dumps(cli(sys.argv[5],json.loads(sys.argv[6]) if len(sys.argv)>6 else {}),indent=2))
elif mode=='show':cli('ui.show',{'view':sys.argv[5]});time.sleep(1.2);photo('show-'+sys.argv[5])
elif mode=='capture-click':
 name=sys.argv[5];x,y=map(int,sys.argv[6:8]);head=int(sys.argv[8]) if len(sys.argv)>8 else 0
 before={v['id'] for v in cli('operation.recent')['operations']};began=time.monotonic();click(x,y);time.sleep(.6);photo(name+'-countdown',head)
 rows=[v for v in cli('operation.recent')['operations'] if v['id'] not in before];assert len(rows)==1,rows
 r=wait(rows[0]['id']);save(name,cli('operation.inspect',{'id':rows[0]['id']}));assert r['state']=='completed',r;im=fetch(r['path']);im.save(E/(name+'-image.png'));photo(name+'-after',head);print(name,r,'elapsed',time.monotonic()-began,flush=True)
elif mode=='cancel-click':
 op,_=start('monitor',10);time.sleep(.7);photo('click-cancel-before',int(sys.argv[7]) if len(sys.argv)>7 else 0);click(int(sys.argv[5]),int(sys.argv[6]));r=wait(op);save('click-cancel',cli('operation.inspect',{'id':op}));photo('click-cancel-after');assert r['code']=='cancelled',r;print('click countdown cancellation passed',flush=True)
elif mode=='restart':
 cli('ui.quit');time.sleep(2)
 if desktop=='hyprland':guest(ENV+'setsid -f /usr/bin/putgd --background >/tmp/acceptance-resident-restart.log 2>&1 </dev/null')
 else:
  restarted=lab('start','--run',RUN);print({'restartStatus':restarted.get('status'), 'error':restarted.get('error')})
 time.sleep(3);move(400,400);cli('ui.show',{'view':'settings'});time.sleep(1.5);photo('restart-settings')
elif mode=='bind':
 rx,ry,mx,my=map(int,sys.argv[5:9]);click(rx,ry);time.sleep(.5);key('ctrl','alt','r');time.sleep(1.5);click(mx,my);time.sleep(.5);key('ctrl','alt','m');time.sleep(3);photo('shortcuts-bound')
 doc=save('bound-settings',cli('settings.get'));assert doc['document']['actions']['repeat']['shortcut']=='Ctrl+Alt+R';assert doc['document']['actions']['monitor']['shortcut']=='Ctrl+Alt+M';save('bound-capabilities',cli('capabilities'));print('both shortcut bindings persisted',flush=True)
elif mode=='keys':
 settings=cli('settings.get');cli('settings.patch',{'patch':{'preferences':{'notifications':True}},'expectedRevision':settings['metadata']['observedRevision']});time.sleep(1)
 for _ in range(30):
  caps=cli('capabilities');bindings=caps.get('source',{}).get('shortcuts',{}).get('bindings',{})
  if all(bindings.get(a,{}).get('bound') for a in ['repeat','monitor']):break
  time.sleep(.5)
 save('bound-capabilities',caps);assert all(bindings.get(a,{}).get('bound') for a in ['repeat','monitor']),bindings;photo('shortcuts-bound')
 r=keyop(('ctrl','alt','r'),'key-repeat-empty');time.sleep(.7);photo('key-repeat-empty');assert r['code']=='repeat_unavailable',r
 ox,oy=ORIGIN[1];move(ox+400,oy+400);r=keyop(('ctrl','alt','m'),'key-monitor-head1');im=fetch(r['path']);im.save(E/'key-monitor-head1.png');assert im.size==(1024,768),im.size;print('real repeat refusal + monitor key head1 passed',flush=True)
elif mode=='delayed-region':
 before={v['id'] for v in cli('operation.recent')['operations']};click(int(sys.argv[5]),int(sys.argv[6]));time.sleep(1);photo('rail-region-selector');drag(300,300,600,500);released=time.monotonic();time.sleep(.5);photo('rail-region-countdown');(E/'capture-helper-qt.txt').write_text(guest("pid=$(pgrep -xo putgd-capture); if [ -n \"$pid\" ]; then readlink /proc/$pid/exe; awk '/libQt6Core.so/{print $6}' /proc/$pid/maps | sort -u; fi"));rows=[v for v in cli('operation.recent')['operations'] if v['id'] not in before];assert len(rows)==1,rows;r=wait(rows[0]['id']);save('rail-region-delayed',cli('operation.inspect',{'id':rows[0]['id']}));im=fetch(r['path']);im.save(E/'rail-region-delayed.png');assert im.size==(300,200);assert time.monotonic()-released>=2.8;print('window-menu delayed region passed',flush=True)
elif mode=='quiet':
 settings=cli('settings.get');cli('settings.patch',{'patch':{'preferences':{'notifications':False}},'expectedRevision':settings['metadata']['observedRevision']});time.sleep(1);print('notifications disabled')
elif mode=='bind-one':
 click(int(sys.argv[5]),int(sys.argv[6]));time.sleep(.5);key('ctrl','alt',sys.argv[7]);time.sleep(3);photo('bound-'+sys.argv[7]);save('settings-bound-'+sys.argv[7],cli('settings.get'));save('capabilities-bound-'+sys.argv[7],cli('capabilities'))
elif mode=='route-proof':
 original=cli('settings.get');doc=original['document'];assert doc['actions']['monitor']['destination']=='local',doc['actions']['monitor'];assert 'captureDefaults' in doc,doc
 profile=cli('settings.developmentTemplate')['document']['profiles'][0];profile.update(id='acceptance-unavailable',label='Synthetic unavailable route');profile['credentials']['reference']='putgd/acceptance-1363-unavailable';profile['settings'].update(bucket='synthetic-capture-1363',endpoint='https://127.0.0.1:1',publicUrlBase=None,aclMode='omit')
 cli('settings.patch',{'patch':{'profiles':[profile],'captureDefaults':{'destination':'upload','profileId':profile['id'],'publicationMode':'default'},'preferences':{'unlockCredentialsAtStartup':False}},'expectedRevision':original['metadata']['observedRevision']});time.sleep(2)
 try:
  save('different-default-route',cli('settings.get'));move(400,400);op,_=start('monitor');r=wait(op);d=save('monitor-exception-result',cli('operation.inspect',{'id':op}));assert r['state']=='completed' and not d['destination'].get('profileId'),d;fetch(r['path']).save(E/'monitor-exception-result.png');photo('monitor-exception-with-different-default');print('GUI monitor exception overrides unavailable synthetic upload default',flush=True)
 finally:
  current=cli('settings.get');cli('settings.patch',{'patch':{'profiles':doc['profiles'],'captureDefaults':doc['captureDefaults'],'preferences':{'unlockCredentialsAtStartup':doc['preferences'].get('unlockCredentialsAtStartup',True),'notifications':False}},'expectedRevision':current['metadata']['observedRevision']})
elif mode=='scroll':
 move(int(sys.argv[5]),int(sys.argv[6]));button_name='wheel-down' if int(sys.argv[7])<0 else 'wheel-up'
 for _ in range(abs(int(sys.argv[7]))):qmp([{'type':'btn','data':{'down':True,'button':button_name}},{'type':'btn','data':{'down':False,'button':button_name}}]);time.sleep(.08)
 time.sleep(.8);photo(sys.argv[8],int(sys.argv[9]) if len(sys.argv)>9 else 0)
elif mode=='verify-pill':
 name=sys.argv[5];box=tuple(map(int,sys.argv[6:10]));head=int(sys.argv[10]) if len(sys.argv)>10 else 0
 shown=Image.open(E/(name+'-countdown.png')).convert('RGB').crop(box);clean=Image.open(E/(name+'-after.png')).convert('RGB').crop(box);image=Image.open(E/(name+'-image.png')).convert('RGB');assert image.size==SIZE[head],image.size
 captured=image.crop(box);a=differs(captured,clean);b=differs(captured,shown);save(name+'-pill-omission',{'box':box,'capturedVsClean':a,'capturedVsCountdown':b,'pass':a<2 and b>8});assert a<2 and b>8,(a,b);print('countdown omitted from image',a,b,flush=True)
elif mode=='capture-cancel':
 name=sys.argv[5];x,y,px,py=map(int,sys.argv[6:10]);head=int(sys.argv[10]) if len(sys.argv)>10 else 0
 before={v['id'] for v in cli('operation.recent')['operations']};click(x,y);time.sleep(.5);photo(name+'-before',head);rows=[v for v in cli('operation.recent')['operations'] if v['id'] not in before];assert len(rows)==1,rows
 click(px,py);r=wait(rows[0]['id']);save(name,cli('operation.inspect',{'id':rows[0]['id']}));photo(name+'-after',head);assert r['code']=='cancelled',r;print('GUI-started countdown cancelled by clicking pill',flush=True)
elif mode=='fetch-op':
 d=save(sys.argv[6],cli('operation.inspect',{'id':sys.argv[5]}));assert d['state']=='completed',d;fetch(d['items'][0]['local']['path']).save(E/(sys.argv[6]+'.png'))
elif mode=='warmup':
 settings=cli('settings.get');cli('settings.patch',{'patch':{'preferences':{'captureDelaySeconds':3,'notifications':False},'archive':{'keepUploads':True}},'expectedRevision':settings['metadata']['observedRevision']});time.sleep(2)
 cli('ui.show',{'view':'settings'});time.sleep(1);key('alt','f4');time.sleep(1)
 old={v['id'] for v in cli('operation.recent')['operations']};key('ctrl','shift','1');time.sleep(.7);photo('warmup-plain-shortcut-selector');drag(300,300,600,500);released=time.monotonic();rows=[v for v in cli('operation.recent')['operations'] if v['id'] not in old];assert len(rows)==1,rows;r=wait(rows[0]['id']);d=save('warmup-plain-shortcut-region',cli('operation.inspect',{'id':rows[0]['id']}));im=fetch(r['path']);im.save(E/'warmup-plain-shortcut-region.png');elapsed=time.monotonic()-released;assert im.size==(300,200) and elapsed<2.8,(im.size,elapsed)
 op,_=start('region',3);time.sleep(.8);photo('warmup-delayed-selector');drag(300,300,600,500);released=time.monotonic();time.sleep(.6);photo('warmup-delayed-countdown');qt=guest("pid=$(pgrep -xo putgd-capture); if [ -n \"$pid\" ]; then readlink /proc/$pid/exe; awk '/libQt6Core.so/{print $6}' /proc/$pid/maps | sort -u; fi");(E/'warmup-helper-loaded-qt.txt').write_text(qt);r=wait(op);save('warmup-delayed-region',cli('operation.inspect',{'id':op}));im=fetch(r['path']);im.save(E/'warmup-delayed-region.png');after=time.monotonic()-released;assert im.size==(300,200) and after>=2.8,(im.size,after)
 save('warmup-results',{'passed':True,'plainShortcutAfterDragSeconds':elapsed,'delayedAfterDragSeconds':after,'loadedHelperQt':qt,'diagnostics':cli('diagnostics')});print('Qt warm-up intersection: real shortcut immediate, delayed region3s passed',flush=True)
