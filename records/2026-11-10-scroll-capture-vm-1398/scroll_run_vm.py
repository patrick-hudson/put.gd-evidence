#!/usr/bin/env python3
"""Pinned-package scroll acceptance. Run on a builder with its desktop lease held.

Existing private resident required. Example:
 python3 scroll_run.py --socket /tmp/sc/runtime/putgd/session.sock --out /tmp/sc/r1 \
   --package /tmp/package.deb --rect 0,100,1800,600 --rows 60 \
   --open firefox --page /tmp/ruler.html --png-root /tmp/sc/data
--open launches only the supplied ruler page; omit it for an already open fixture.
The HTML format is probes/scripts/ruler.html (white=1); --format fixture verifies
ScrollRuler.h's per-pixel-line pattern (dark=1). --code-width is the original page
width when a capture excludes its scrollbar. Preserve logs and PNG even on failure.
No configuration is changed. No input is sent by this driver beyond scroll.*.
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, time, shlex
from pathlib import Path


def digest(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()


def pattern(row,line):
    if line<2:return 65535
    if line<30:return row
    x=(row*2654435761+line*40503+0x9e3779b9)&0xffffffff
    x^=x>>15;x=x*0x2c1b3c6d&0xffffffff;x^=x>>12;x=x*0x297a2d39&0xffffffff;x^=x>>15
    b=x&65535
    return b if b not in (0,65535) else 0x5a5a^line


def verify(path,a):
    from PIL import Image
    im=Image.open(path).convert('RGB');w,h=im.size;s=a.scale
    expected=a.height or round((a.rows*40-a.first_pixel+a.header+a.footer)*s)
    errors=[]
    if h!=expected:errors.append('height %d expected %d'%(h,expected))
    width=a.code_width or w/s
    cell=(int(width)-76)//16 if a.format=='fixture' else (width-a.scrollbar)/16
    left=64 if a.format=='fixture' else 0
    # Every output scanline, three interior points per cell. This catches seam
    # errors at finer resolution than sampling once per 40px row.
    for y in range(h):
        logical=int(y/s)
        if logical<a.header or logical>=h/s-a.footer:
            want=(32,80,128) if logical<a.header else (128,96,32)
            for c in range(16):
                got=im.getpixel((min(w-1,round((left+(c+.5)*cell)*s)),y))
                if max(abs(got[i]-want[i]) for i in range(3))>8:
                    errors.append('sticky band mismatch at line %d'%y);break
        else:
            pos=a.first_pixel+logical-a.header;row,line=divmod(pos,40)
            bits=pattern(row,line) if a.format=='fixture' else row
            for c in range(16):
                for frac in (.25,.5,.75):
                    x=min(w-1,int((left+(c+frac)*cell)*s));got=im.getpixel((x,y))
                    # HTML labels occupy leftmost 100 CSS px on the first 23 lines.
                    if a.format=='html' and x/s<100 and line<24:continue
                    one=(bits>>(15-c))&1
                    want=(16 if one else 250) if a.format=='fixture' else (255 if one else 0)
                    if max(abs(v-want) for v in got)>12:
                        errors.append('pixel (%d,%d) row %d line %d got %s expected %d'%(x,y,row,line,got,want));break
                if errors and errors[-1].startswith('pixel'):break
        if len(errors)>=12:break
    # Full cell interiors below labels: cursor, ring and bar contamination adds
    # non-ruler pixels. This deliberately excludes text/scrollbar columns.
    contamination=0
    for y in range(h):
        ly=int(y/s)
        if ly<a.header or ly>=h/s-a.footer:continue
        pos=a.first_pixel+ly-a.header;row,line=divmod(pos,40)
        bits=pattern(row,line) if a.format=='fixture' else row
        for c in range(16):
            lo=int((left+(c+.12)*cell)*s);hi=min(w,int((left+(c+.88)*cell)*s))
            if a.format=='html' and line<24:lo=max(lo,int(100*s))
            one=bits>>(15-c)&1;want=(16 if one else 250) if a.format=='fixture' else (255 if one else 0)
            for x in range(lo,hi):
                if max(abs(v-want) for v in im.getpixel((x,y)))>12:contamination+=1
    if contamination:errors.append('%d unexpected pixels in barcode interiors (cursor/overlay or wrong content)'%contamination)
    return {'pass':not errors,'size':[w,h],'expectedHeight':expected,'errors':errors,'unexpectedPixels':contamination,
            'coverage':'every scanline; full barcode cell interiors excluding labels, cell edges and scrollbar; visual check still required outside barcode'}


def main():
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--socket');p.add_argument('--cli',default='putgd-cli');p.add_argument('--out',required=True)
    p.add_argument('--package',required=True);p.add_argument('--rect',type=lambda v:list(map(int,v.split(','))))
    p.add_argument('--rows',type=int,default=60);p.add_argument('--first-pixel',type=int,default=0)
    p.add_argument('--height',type=int);p.add_argument('--header',type=int,default=0);p.add_argument('--footer',type=int,default=0)
    p.add_argument('--scale',type=float,default=1);p.add_argument('--code-width',type=int);p.add_argument('--scrollbar',type=int,default=0)
    p.add_argument('--format',choices=['html','fixture'],default='html');p.add_argument('--max-height',type=int)
    p.add_argument('--expect-end',default='end_of_content');p.add_argument('--control',choices=['stop','cancel']);p.add_argument('--after',type=float,default=3)
    p.add_argument('--open',help='shell-quoted argv, executed without a shell');p.add_argument('--page');p.add_argument('--png-root',action='append',default=[])
    p.add_argument('--verify-png');p.add_argument('--timeout',type=float,default=240)
    a=p.parse_args();out=Path(a.out).resolve();out.mkdir(mode=0o700,parents=True,exist_ok=False)
    result={'host':os.uname().nodename,'prHead':'fe8cd713a22f2c68207de76e43da5f0e56d95243','mergeCommit':'e3c1bd6b840a0aae351918bd4c6ef481bfa82d88','run':42897860301,'package':str(Path(a.package).resolve()),'packageSha256':digest(a.package),'arguments':vars(a)}
    browser=None;ident=None;terminal=False
    def call(method,params=None):
        cmd=[a.cli]+(['--socket',a.socket] if a.socket else [])+[method,json.dumps(params or {})]
        r=subprocess.run(cmd,text=True,capture_output=True,timeout=65)
        obj=json.loads(r.stdout)
        with open(out/'rpc.jsonl','a') as f:f.write(json.dumps({'time':time.time(),'method':method,'params':params,'reply':obj,'stderr':r.stderr})+'\n')
        if not obj.get('ok'):raise RuntimeError('%s: %s'%(method,obj.get('error')))
        return obj['result']
    try:
        if a.verify_png:
            shutil.copyfile(a.verify_png,out/'capture.png');result['verification']=verify(out/'capture.png',a)
        else:
            sock=Path(a.socket or (os.environ.get('XDG_RUNTIME_DIR','/run/user/%d'%os.getuid())+'/putgd/session.sock')).resolve()
            if len(str(sock).encode())>107:raise RuntimeError('overlong Unix socket: %d bytes'%len(str(sock).encode()))
            result['socketBytes']=len(str(sock).encode());result['build']=json.loads(subprocess.check_output([a.cli,'--version-json'],text=True))
            before=call('history.list',{'limit':200});result['historyBefore']=before
            if a.open:
                if not a.page:raise RuntimeError('--open requires --page')
                browser=subprocess.Popen(shlex.split(a.open)+[Path(a.page).resolve().as_uri()],stdout=open(out/'browser.log','w'),stderr=subprocess.STDOUT);result['browserPid']=browser.pid;time.sleep(4)
            params={}
            if a.rect:params['rect']=a.rect
            if a.max_height:params['maxHeight']=a.max_height
            prepared=call('scroll.prepare',params);ident=prepared['id'];result['id']=ident
            deadline=time.monotonic()+a.timeout
            while prepared['state']!='ready':
                if time.monotonic()>deadline:raise TimeoutError('prepare')
                time.sleep(.2);prepared=call('scroll.inspect',{'id':ident})
            call('scroll.start',{'id':ident});start=time.monotonic();controlled=False
            while True:
                state=call('scroll.inspect',{'id':ident});result['capture']=state
                if state['state'] in ('done','failed','cancelled'):terminal=True;break
                if a.control and not controlled and time.monotonic()-start>=a.after:
                    call('scroll.'+a.control,{'id':ident});controlled=True
                if time.monotonic()>deadline:raise TimeoutError('capture')
                time.sleep(.25)
            if state['state']=='cancelled':
                after=call('history.list',{'limit':200});result['historyAfter']=after
                result['pass']=before==after;result['stagingCheck']='caller must inspect private data/scroll for remaining files'
            elif state['state']!='done':raise RuntimeError('capture failed: '+str(state))
            else:
                sha=state['result']['sha256'];found=None
                for _ in range(60):
                    for root in a.png_root:
                        for candidate in Path(root).rglob('*'):
                            if candidate.is_file() and candidate.suffix.lower()=='.png' and digest(candidate)==sha:found=candidate;break
                        if found:break
                    if found:break
                    time.sleep(.5)
                if not found:raise RuntimeError('PNG not found by reported SHA256; specify private archive/data with --png-root')
                shutil.copyfile(found,out/'capture.png');result['pngSha256']=sha;result['verification']=verify(out/'capture.png',a)
                result['pass']=result['verification']['pass'] and state.get('endReason')==a.expect_end
                result['historyAfter']=call('history.list',{'limit':200})
    except Exception as e:result['pass']=False;result['error']=str(e)
    finally:
        if ident and not terminal:
            try:result['cleanupCancel']=call('scroll.cancel',{'id':ident})
            except Exception as e:result['cleanupError']=str(e)
        if browser and browser.poll() is None:
            browser.terminate()
            try:browser.wait(timeout=10)
            except subprocess.TimeoutExpired:result['browserCleanup']='still running; recorded PID needs inspection'
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return 0 if result.get('pass',result.get('verification',{}).get('pass',False)) else 1
if __name__=='__main__':sys.exit(main())
