#!/usr/bin/env python3
"""Native-desktop candidate recording check. Uses the lab cover, resident, and virtual microphone helpers unchanged."""
import argparse, json, os, re, subprocess as sp, sys, time, traceback, hashlib
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from PIL import Image
import record_run as rr
import rfb
import desktop_lock

TREE='07d9da15d2e97dfbdb9d9ec3ca6f011b3582e416'
W,H=768,432

def call(cmd, **kw):
    try: return sp.run(list(map(str,cmd)), check=True, **kw)
    except sp.CalledProcessError as e:
        if e.stderr: print(e.stderr[-2000:].decode(errors='replace') if isinstance(e.stderr,bytes) else e.stderr[-2000:],file=sys.stderr)
        raise

def ff(*args, **kw):
    return call(['ffmpeg','-hide_banner','-nostdin','-v','error','-threads','2',*args], **kw)

def probe(path):
    return json.loads(call(['ffprobe','-v','error','-show_streams','-show_format','-count_frames','-of','json',path],capture_output=True).stdout)

def fixture(run):
    for name, pattern, extra in [('bars','smpte100',['horizontal-speed=6']),('ball','ball',[])]:
        call(['gst-launch-1.0','-q','videotestsrc','num-buffers=900','pattern='+pattern,*extra,'!',
              'video/x-raw,width=256,height=216,framerate=30/1','!','videoconvert','!','jpegenc','!','matroskamux','!','filesink','location='+str(run/(name+'.mkv'))])
    # A 512x432 white flash at each second boundary with a 100ms 1kHz burst into the virtual microphone.
    ff('-f','lavfi','-i','color=c=black:s=512x432:r=30:d=30','-i',run/'bars.mkv','-i',run/'ball.mkv',
       '-f','lavfi','-i',r"aevalsrc=if(lt(mod(t\,1)\,0.1)\,0.7*sin(2*PI*1000*t)\,0):s=48000:d=30",
       '-filter_complex_threads','2','-filter_complex',"[0:v]drawbox=x=0:y=0:w=iw:h=ih:color=white:t=fill:enable='lt(mod(t,1),0.1)'[m];[1:v][2:v]vstack[b];[m][b]hstack[v]",'-map','[v]','-map','3:a','-c:v','mjpeg','-q:v','3','-c:a','pcm_s16le','-t','30',run/'moving.mkv')
    ff('-ss','1.4','-i',run/'moving.mkv','-frames:v','1',run/'still.png')
    ff('-loop','1','-framerate','30','-i',run/'still.png','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-c:v','mjpeg','-q:v','3','-c:a','pcm_s16le','-t','10',run/'static.mkv')

class Driver(rr.Driver):
    def open_fixture(self, moving):
        marker=self.run/'marker.mkv'
        marker.unlink(missing_ok=True)
        marker.symlink_to(self.run/('moving.mkv' if moving else 'static.mkv'))
        return self.open_cover()

    def review(self,rid,action,**params):
        r=self.cli(self.build,'recording.review',dict(id=rid,action=action,**params))
        self.receipt.setdefault('reviewActions',[]).append({'action':action,'params':params,'reply':r})
        self.save_receipt()
        return r

    def save_receipt(self):
        (self.run/'receipt.json').write_text(json.dumps(self.receipt,indent=2)+'\n')

    def capture(self,moving):
        self.receipt['movingCover' if moving else 'staticCover']=self.open_fixture(moving)
        try:
            req={'target':{'kind':'monitor'},'format':'mp4','codec':'h264','fps':30,'audio':{'system':moving,'microphone':moving}}
            if moving: req['audio']['microphoneDevice']=self.microphone_device()
            r=self.cli(self.build,'recording.prepare',req); rid=r['recordingId']
            self.receipt['movingId' if moving else 'staticId']=rid
            ready=self.wait_state(self.build,rid,('ready',),120)
            self.receipt['movingReady' if moving else 'staticReady']=ready
            self.cli(self.build,'recording.overlay',{'id':rid,'visible':False})
            time.sleep(6 if moving else 1)
            start=self.cli(self.build,'recording.start',{'id':rid}); time.sleep(2)
            progress=self.cli(self.build,'recording.inspect',{'id':rid})
            self.receipt['movingProgress' if moving else 'staticProgress']=progress
            if moving: self.receipt['audioSourcesFromServer']=self.recording_sources()
            time.sleep(10 if moving else 2)
            stopped=self.cli(self.build,'recording.stop',{'id':rid},timeout=60)
            self.receipt['movingStopped' if moving else 'staticStopped']=stopped
            self.save_receipt()
            return rid, stopped
        except Exception:
            self.close_cover(); raise

    def export(self,rid,name,fmt,codec=None):
        if codec is None: codec={'mp4':'h264','webm':'vp9','gif':'','webp':''}[fmt]
        self.review(rid,'format',format=fmt,codec=codec)
        path=self.run/'out'/f'{name}.{fmt}'
        self.cli(self.build,'recording.saveCopy',{'id':rid,'path':str(path),'overwrite':False})
        done=self.wait_state(self.build,rid,('reviewing',),600)
        self.receipt.setdefault('exports',{})[name]={'path':str(path),'reply':done}
        self.save_receipt()
        if (done.get('lastExport') or {}).get('status')!='saved' or not path.is_file(): raise RuntimeError(f'{name} failed: {done.get("lastExport")}')
        return path

    def cancel(self,rid):
        self.cli(self.build,'recording.cancel',{'id':rid}); self.close_cover()
        self.cover=None


def fraction(im):
    ar=np.asarray(im.convert('RGB').resize((160,90))).astype(np.int16)
    return float(np.mean((ar[:,:,0]>180)&(ar[:,:,1]<75)&(ar[:,:,2]>180)))

def check_frame(run, path, im):
    im.save(path)
    p=sp.run([sys.executable,str(rr.HERE/'cover_player.py'),'check-frame',str(path),'--min-fraction','0.5'],capture_output=True,text=True)
    result=json.loads(p.stdout or '{}')
    if p.returncode: raise RuntimeError(f'frame did not pass covered-output check: {result}')
    return result

def parse_fps(stream):
    n,d=map(int,stream['avg_frame_rate'].split('/')); return n/d if d else 0

def stats(path,run,geom,canvas,mask=None):
    name=path.stem; anim=path.suffix in ('.gif','.webp')
    data={'sha256':rr.sha256(path),'bytes':path.stat().st_size}
    if anim:
        im=Image.open(path); size=im.size; source=[]; times=[]; total=0
        frames=[]; mincover=1
        count=im.n_frames
        for i in range(count):
            im.seek(i); rgb=im.convert('RGB'); times.append(total); total+=im.info.get('duration',0)/1000
            mincover=min(mincover,fraction(rgb)); frames.append(np.asarray(rgb.convert('L').resize((160,90))).copy())
            if i in (0,count//2,count-1): check_frame(run,run/'frames'/f'{name}-{i}.png',rgb)
        data.update(duration=total,frameCount=count,size=size,streams=['video only'],minCoverFraction=mincover,decode='Pillow all frames')
        a=np.asarray(frames).astype(np.float32)
    else:
        p=probe(path); data['probe']=p
        v=next(s for s in p['streams'] if s['codec_type']=='video'); size=(v['width'],v['height'])
        fps=parse_fps(v); count=int(v['nb_read_frames']); duration=float(p['format']['duration'])
        # All video frames decoded with -xerror, and all audio decoded separately below.
        raw=ff('-xerror','-i',path,'-map','0:v:0','-vf','scale=160:90:flags=area','-pix_fmt','rgb24','-fps_mode','passthrough','-f','rawvideo','-',capture_output=True).stdout
        ar=np.frombuffer(raw,np.uint8).reshape(-1,90,160,3).astype(np.int16)
        mincover=float(np.min(np.mean((ar[:,:,:,0]>180)&(ar[:,:,:,1]<75)&(ar[:,:,:,2]>180),axis=(1,2))))
        a=(ar[:,:,:,0]*0.299+ar[:,:,:,1]*0.587+ar[:,:,:,2]*0.114).astype(np.float32)
        data.update(duration=duration,frameCount=len(a),probeFrameCount=count,size=size,streams=[(s['codec_type'],s['codec_name']) for s in p['streams']],minCoverFraction=mincover,decode='distro FFmpeg all frames')
        for i,t in enumerate([0.2,duration/2,max(0,duration-0.2)]):
            img=run/'frames'/f'{name}-{i}.png'
            ff('-ss',str(t),'-i',path,'-frames:v','1',img)
            with Image.open(img) as im: rgb=im.convert('RGB')
            check_frame(run,img,rgb)
        if any(s['codec_type']=='audio' for s in p['streams']):
            raw=ff('-xerror','-i',path,'-map','0:a:0','-ac','1','-ar','48000','-f','f32le','-',capture_output=True).stdout
            audio=np.frombuffer(raw,np.float32); assert len(audio)>4800
            rms=float(np.sqrt(np.mean(audio*audio)))
            # Each 10 ms audio window: 440Hz system output and 1000Hz microphone.
            chunks=audio[:len(audio)//480*480].reshape(-1,480); t=np.arange(480)/48000
            bands={str(hz): abs(chunks@np.exp(-2j*np.pi*hz*t))*2/480 for hz in [440,1000]}
            data['audio']={'meanVolumeDb':round(20*np.log10(max(rms,1e-10)),2),'duration':len(audio)/48000,
                'peak440':float(np.max(bands['440'])),'median440':float(np.median(bands['440'])),'peak1000':float(np.max(bands['1000']))}
            # Locate the marker's white flashes in its own inset, using the actual frame PTS reported by ffprobe.
            x=(geom[2]-W)/2+W/3; y=geom[3]/2
            px,py=round(x/geom[2]*160),round(y/geom[3]*90)
            lum=a[:,max(0,py-2):py+3,max(0,px-2):px+3].mean(axis=(1,2)); bright=lum>170
            indices=np.flatnonzero(bright & ~np.r_[False,bright[:-1]])
            fp=json.loads(call(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',path],capture_output=True).stdout)['frames']
            pts=np.array([float(f['best_effort_timestamp_time']) for f in fp])
            audio_stream=next(s for s in p['streams'] if s['codec_type']=='audio'); start=float(audio_stream.get('start_time',0)); ba=bands['1000']>max(.02,float(np.max(bands['1000']))*.25)
            burst=np.flatnonzero(ba & ~np.r_[False,ba[:-1]])*.01+start
            flash=pts[indices] if len(pts)==len(a) else indices/fps
            offsets=[float((burst[np.argmin(abs(burst-f))]-f)*1000) for f in flash if len(burst) and min(abs(burst-f))<.4]
            data['audio'].update(flashes=flash.tolist(),bursts=burst.tolist(),offsetsMs=offsets,medianOffsetMs=float(np.median(offsets)) if offsets else None,maxAbsOffsetMs=max(map(abs,offsets)) if offsets else None)
    data['motionMeanAdjacent']=float(np.mean(np.abs(np.diff(a,axis=0)))) if len(a)>1 else 0
    data['motionMeanLag1s']=float(np.mean(np.abs(a[15:]-a[:-15]))) if len(a)>15 else 0
    if data['minCoverFraction']<.45: raise RuntimeError(f'{name}: frame coverage dropped below .45: {data["minCoverFraction"]}')
    return data

def blur_score(path,t,rect,canvas):
    p=probe(path); v=next(s for s in p['streams'] if s['codec_type']=='video'); width,height=v['width'],v['height']
    x,y,w,h=rect; sx,sy=width/canvas[0],height/canvas[1]
    raw=ff('-ss',str(t),'-i',path,'-frames:v','1','-pix_fmt','gray','-f','rawvideo','-',capture_output=True).stdout
    a=np.frombuffer(raw,np.uint8).reshape(height,width).astype(float)
    crop=a[int((y+8)*sy):int((y+h-8)*sy),int((x+8)*sx):int((x+w-8)*sx)]
    return float(np.mean(np.abs(np.diff(crop,axis=1))))

def wall_frame(d, name):
    # The lab cover is already proven and still active. The same frame gate checks the screenshot before retention.
    c=rfb.RFB(d.args.vnc_port)
    try: w,h,pixels=c.frame()
    finally: c.close()
    im=Image.frombytes('RGB',(w,h),pixels,'raw','BGRX')
    if fraction(im)<.5: raise RuntimeError('wall frame not at least half synthetic cover; not saved')
    path=d.run/'frames'/f'{name}.png'
    return check_frame(d.run,path,im)

def player(d,path):
    # Actual native desktop playback; ffplay is a real player. Preserve a timestamp and its result.
    cmd=['ffplay','-fs','-autoexit','-loglevel','error','-window_title','FFmpeg 9.1 acceptance: '+path.name,'-x','960','-y','540',str(path)]
    p=sp.Popen(cmd,env=d.env,stdout=sp.DEVNULL,stderr=sp.PIPE,text=True)
    time.sleep(2); running=p.poll() is None
    images=[]
    if running:
        for i in range(2):
            try: images.append(wall_frame(d,f'player-{path.stem}-{i}'))
            except Exception as e: images.append({'error':str(e)})
            time.sleep(0.5)
    try: _,err=p.communicate(timeout=30)
    except sp.TimeoutExpired: p.terminate(); _,err=p.communicate(timeout=5)
    return {'player':'ffplay','wasPlayingAfter2s':running,'exit':p.returncode,'stderr':err,'file':path.name,'wallFrames':images}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('run'); ap.add_argument('image'); ap.add_argument('--port',type=int,required=True); ap.add_argument('--tree',default=TREE); ap.add_argument('--real-data-home',action='store_true'); args=ap.parse_args()
    desktop_lock.refuse_unless_held('ffmpeg91 acceptance'); desktop_lock.refuse_while_quiet('ffmpeg91 acceptance')
    run=Path(args.run).resolve(); run.mkdir(mode=0o700); image=Path(args.image).resolve()
    a=SimpleNamespace(run=str(run),analyzer=str(run/'appdir-candidate/squashfs-root'),real_data_home=args.real_data_home,
        mic='virtual',system='tone',mic_default=False,cards_off=False,audio_device=None,video='marker',output=None,video_size='768x432',click=[],vnc_port=args.port,precheck_wait=2,no_notifications=True)
    d=Driver(a); assert len(os.fsencode(d.socket))<=107
    d.env['PUTGD_RECORD_DEBUG_LOG']=str(run/'logs/record.log')
    d.receipt={'host':os.uname().nodename,'session':d.env.get('XDG_SESSION_TYPE'),'desktop':d.desktop,'socket':str(d.socket),'socketBytes':len(os.fsencode(d.socket)),'expectedTree':args.tree,'exports':{},'stats':{},'errors':[]}
    try:
        if d.desktop=='gnome-shell':
            ext=call(['gnome-extensions','list','--enabled'],env=d.env,capture_output=True,text=True).stdout
            assert 'appindicatorsupport@rgcjonas.gmail.com' in ext
            d.receipt['gnomeTrayEnabled']=True
        d.build=rr.Build('candidate',image,run); d.receipt['identity']=d.build.identity
        fixture(run)
        d.receipt['osRelease']=Path('/etc/os-release').read_text()
        d.receipt['kernel']=os.uname().release
        d.receipt['desktopVersion']=sp.run([d.desktop,'--version'],env=d.env,capture_output=True,text=True,timeout=15).stdout.strip()
        d.receipt['capabilities']=d.start_resident(d.build)
        diag=d.cli(d.build,'diagnostics'); d.receipt['build']=diag.get('build')
        assert diag.get('build',{}).get('gitTree')==args.tree, d.receipt['build']
        time.sleep(4); d.stop_resident(d.build)
        d.receipt['microphone']=d.open_microphone(); d.start_resident(d.build)
        rid,stop=d.capture(False); path=d.export(rid,'control','mp4'); geom=d.cover_rect; canvas=stop['canvas']; d.cancel(rid)
        d.receipt['stats']['control']=stats(path,run,geom,canvas); d.save_receipt()
        rid,stop=d.capture(True); geom=d.cover_rect; canvas=stop['canvas']; d.receipt['canvas']=canvas
        for fmt in ['mp4','webm','gif','webp']:
            try:
                path=d.export(rid,fmt,fmt); d.receipt['stats'][fmt]=stats(path,run,geom,canvas)
                control=d.receipt['stats']['control']; row=d.receipt['stats'][fmt]
                if row['motionMeanLag1s'] <= max(control['motionMeanLag1s']*3,0.6): raise RuntimeError('moving clip does not exceed frozen control')
                if fmt in ('mp4','webm'):
                    audio=row.get('audio',{}); codecs=dict(row['streams'])
                    assert codecs.get('video') in ({'h264','hevc'} if fmt=='mp4' else {'vp9'}) and codecs.get('audio')==('aac' if fmt=='mp4' else 'opus'), codecs
                    assert audio.get('meanVolumeDb',-200)>-70 and audio.get('median440',0)>.001 and audio.get('peak1000',0)>.01, audio
                else: assert row['frameCount']>1
            except Exception as e: d.receipt['errors'].append({'row':fmt,'error':str(e)})
            d.save_receipt()
        try:
            # Trim 1 second each end; cut 2 seconds in the middle; blur the SMPTE bars only.
            duration=int(stop['durationUs']); d.review(rid,'format',format='mp4',codec='h264')
            d.review(rid,'setTrim',start=1_000_000,end=duration-1_000_000)
            d.review(rid,'selectRange',start=4_000_000,end=6_000_000); d.review(rid,'cut'); d.review(rid,'clearSelection')
            cw,ch=(canvas if isinstance(canvas,list) else [canvas['width'],canvas['height']]); gx,gy,gw,gh=geom
            # 256 x 216 SMPTE pane, centered within the 768x432 fixture; keep the blur inside it.
            x=round(((gw-W)/2+512+16)*cw/gw); y=round(((gh-H)/2+16)*ch/gh); w=round(224*cw/gw); h=round(184*ch/gh)
            mask=[x,y,w,h]; d.receipt['blurRect']=mask
            d.review(rid,'addMask',kind='blur',rect=mask); d.review(rid,'strength',strength=48)
            edited=d.review(rid,'inspect'); d.receipt['editedReview']=edited
            path=d.export(rid,'edited','mp4'); d.receipt['stats']['edited']=stats(path,run,geom,canvas)
            if (run/'out/mp4.mp4').exists():
                before=run/'out/mp4.mp4'; d.receipt['blurScores']=[{'sourceTime':t+1,'editedTime':t,'before':blur_score(before,t+1,mask,[cw,ch]),'after':blur_score(path,t,mask,[cw,ch])} for t in [0.4,0.8,1.4,1.8]]
                assert np.mean([n['after'] for n in d.receipt['blurScores']]) < np.mean([n['before'] for n in d.receipt['blurScores']])*.75, 'blur did not reduce edge contrast'
            editedStats=d.receipt['stats']['edited']; assert abs(editedStats['duration']-edited['outputDurationUs']/1e6)<.2, 'edited export duration mismatch'
            audio=editedStats.get('audio',{}); assert audio.get('meanVolumeDb',-200)>-70 and audio.get('median440',0)>.001 and audio.get('peak1000',0)>.01, audio
            assert len(audio.get('offsetsMs',[]))>=3 and abs(audio['medianOffsetMs'])<200, 'A/V sync not established'
        except Exception as e: d.receipt['errors'].append({'row':'edited','error':str(e)})
        # Corroborate the encoder selection using the candidate helper's supported export diagnostic.
        # The resident's saveCopy receipt does not expose the helper's videoEncoder result.
        working=run/'working'/f'{rid}.mkv'
        d.receipt['encoderDiagnostics']={}
        for fmt in ['mp4','webm','gif','webp']:
            if fmt not in d.receipt['stats']: continue
            cfg=d.receipt['exports'][fmt]['reply']['config']; dest=run/'out'/('encoder-check.'+fmt)
            command=['--export',working,dest,'--trim',0,1_500_000]
            if cfg.get('codec'): command += ['--codec',cfg['codec']]
            if cfg.get('maxEdge'): command += ['--max-edge',cfg['maxEdge']]
            try:
                result=d.helper(*command,timeout=120)
                d.receipt['encoderDiagnostics'][fmt]={'stdout':result.stdout.strip(),'returnCode':result.returncode,'stderr':result.stderr[-1000:]}
                if result.returncode==0: dest.unlink(missing_ok=True)
            except Exception as e: d.receipt['encoderDiagnostics'][fmt]={'error':str(e)}
        d.save_receipt(); d.cli(d.build,'recording.cancel',{'id':rid})
        # The player itself is full-screen synthetic covered output, not the cover underneath it.
        d.close_cover(); d.cover=None
        d.receipt['players']={fmt:player(d,run/'out'/f'{fmt}.{fmt}') for fmt in ['mp4','webm'] if (run/'out'/f'{fmt}.{fmt}').exists()}
        for fmt,row in d.receipt['players'].items():
            if not row['wasPlayingAfter2s'] or row['exit']!=0 or not any(f.get('ok') for f in row['wallFrames']): d.receipt['errors'].append({'row':fmt+' player','error':str(row)})
    except Exception as e:
        traceback.print_exc(); d.receipt['errors'].append({'row':'campaign','error':str(e)})
    finally:
        try: d.stop_resident(d.build) if hasattr(d,'build') else None
        finally:
            try: d.close_cover()
            finally:
                try: d.receipt['micCleanup']=d.close_microphone()
                except Exception as e: d.receipt['errors'].append({'row':'cleanup','error':str(e)})
                if d.real_data is not None and d.real_data.exists(): d.real_data.rename(run/'real-data-putgd')
                d.save_receipt()
    return 1 if d.receipt['errors'] else 0
if __name__=='__main__': sys.exit(main())
