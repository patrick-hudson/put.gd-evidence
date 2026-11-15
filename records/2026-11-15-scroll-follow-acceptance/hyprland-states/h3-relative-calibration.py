import accept as A,subprocess,time,json
P=A.P;mouse=None
try:
 flat=A.remote('flat');A.remote('anchor','960','540');a=A.remote('pointer')
 mouse=subprocess.Popen(['python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert mouse.stdout.readline().startswith('ready')
 mouse.stdin.write('m 100 0\n');mouse.stdin.flush();time.sleep(.2);b=A.remote('pointer')
 mouse.stdin.write('m 0 100\n');mouse.stdin.flush();time.sleep(.2);c=A.remote('pointer')
 r={'flat':flat,'before':a,'after100x':b,'after100y':c,'nativeObserver':'Hyprland cursorpos -j','input':'Real relative uinput in own native Firefox before any capture'};(P/'h3-relative-calibration.json').write_text(json.dumps(r,indent=1));print(json.dumps(r),flush=True);assert[b[0]-a[0],b[1]-a[1],c[0]-b[0],c[1]-b[1]]==[100,0,0,100]
finally:
 if mouse:mouse.stdin.write('q\n');mouse.stdin.flush();mouse.wait(5)
 A.L.browser_stop()
