from pathlib import Path
import ctypes,ctypes.util,json,time,subprocess
l=Path.home()/'work/s5202';v=json.loads((l/'before-state.json').read_text());p=dict(x.split('=',1) for x in v['pointer'].splitlines());x,y=int(p['X']),int(p['Y'])
xl=ctypes.CDLL(ctypes.util.find_library('X11'));xt=ctypes.CDLL(ctypes.util.find_library('Xtst'))
xl.XOpenDisplay.argtypes=[ctypes.c_char_p];xl.XOpenDisplay.restype=ctypes.c_void_p;d=xl.XOpenDisplay(None);assert d
xt.XTestFakeMotionEvent.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ulong];xt.XTestFakeMotionEvent.restype=ctypes.c_int
xt.XTestFakeKeyEvent.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_int,ctypes.c_ulong];xt.XTestFakeKeyEvent.restype=ctypes.c_int
xl.XFlush.argtypes=[ctypes.c_void_p];xl.XSync.argtypes=[ctypes.c_void_p,ctypes.c_int];xl.XCloseDisplay.argtypes=[ctypes.c_void_p]
assert xt.XTestFakeMotionEvent(d,0,x+1,y,0);assert xt.XTestFakeMotionEvent(d,0,x,y,0)
assert xt.XTestFakeKeyEvent(d,50,1,0);assert xt.XTestFakeKeyEvent(d,50,0,0);xl.XSync(d,0);xl.XCloseDisplay(d);time.sleep(.2)
after=subprocess.check_output(['xinput','--list','--long'],text=True);(l/'a/xinput-after-xtest.txt').write_text(after);print('Exact input list restored:',after==v['xinput']);assert after==v['xinput']
