from pathlib import Path
import sys,os,re
p=Path(__file__).parent/'scenario';kind,host=sys.argv[1:3];assert kind in ('native','ai')
label=os.environ.get('B1428_FINAL_LABEL',host+'-'+kind);marker=Path(__file__).parent/('confirm-'+label+'.txt');assert not marker.exists();(p/'mode').write_text('classic')
os.environ.update(PUTGD_REAL_RUNTIME='1',PUTGD_CONFIRM_FIXTURE=str(marker),PUTGD_MEASUREMENT_VNC_PORT=os.environ.get('B1428_VNC_PORT','5901' if host=='f44' else '5900'),PUTGD_MEASUREMENT_SOURCE=str(Path.home()/'work/b1428/r'),PUTGD_LATENCY_ONLY='1')
if os.environ.get('B1428_FINAL_LATENCY')=='1':os.environ['PUTGD_FINAL_LATENCY']='1'
app=str(Path(__file__).parent/'candidate.AppImage') if kind=='ai' else '/usr/bin/putgd';cli=str(Path(__file__).parent/'cli') if kind=='ai' else '/usr/bin/putgd-cli';leaders=['gsd-power','gnome-shell'] if 'gnome' in host or host=='f44' else ['quickshell','Hyprland'] if 'hypr' in host else ['labwc','budgie-daemon'] if 'budgie' in host else ['plasmashell','kwin_wayland','kwin_x11']
a=['python3',str(p/'text_proof.py'),'--desktop',label+'-final3572','--leader',*leaders,'--app',app,'--cli',cli,'--screen','1920','1080','--region','600','430','1400','650','--triggers','hotkey','--fixture','python3',str(p/'fixture.py'),'--expect',re.escape('ALPHA BRAVO CHARLIE\nSYNTHETIC TEXT 1428\nhello@example.test'),'--first-light','--helper-watch',str(p/'helper_watch.py'),'--host-input',str(p/'host_input.py'),'--rfb','none','--settle','3','--input-socket',os.environ.get('B1428_INPUT_SOCKET','start')]
if 'gnome' in host or host=='f44':a.extend(['--first-keys','esc'])
os.execvp(a[0],a)
