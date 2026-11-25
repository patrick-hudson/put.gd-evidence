#!/usr/bin/env python3
"""Capture one native 60 s working clip, then time both exact AppImage helpers on it."""
import json, os, re, sys, time, subprocess as sp, resource, statistics
from pathlib import Path
from types import SimpleNamespace
import desktop_lock
from accept import Driver, rr, TREE, call, ff, probe
import numpy as np

def write(path,d): path.write_text(json.dumps(d,indent=2)+'\n')
def capture(run, image, fixture):
    desktop_lock.refuse_unless_held('AAC capture'); desktop_lock.refuse_while_quiet('AAC capture')
    run.mkdir(mode=0o700)
    a=SimpleNamespace(run=str(run),analyzer=str(run/'appdir-candidate/squashfs-root'),real_data_home=True,
      mic='off',system='tone',mic_default=False,cards_off=False,audio_device=None,video='marker',output=None,video_size='768x432',click=[],vnc_port=5900,precheck_wait=2,no_notifications=True)
    d=Driver(a); assert len(os.fsencode(d.socket))<=107
    d.env['PUTGD_RECORD_DEBUG_LOG']=str(run/'logs/record.log')
    receipt={'socket':str(d.socket),'socketBytes':len(os.fsencode(d.socket)),'host':os.uname().nodename,'desktop':d.desktop,'session':d.env['XDG_SESSION_TYPE'],'errors':[]}
    try:
        d.build=rr.Build('candidate',image,run); receipt['candidate']=d.build.identity
        receipt['capabilities']=d.start_resident(d.build)
        receipt['build']=d.cli(d.build,'diagnostics')['build']; assert receipt['build']['gitTree']==TREE
        time.sleep(4); d.stop_resident(d.build)
        receipt['sound']=d.open_microphone(); a.audio_device=receipt['sound']['systemSink']
        (run/'marker.mkv').symlink_to(fixture)
        d.start_resident(d.build)
        receipt['cover']=d.open_cover()
        req={'target':{'kind':'monitor'},'format':'mp4','codec':'h264','fps':30,'audio':{'system':True,'microphone':False}}
        p=d.cli(d.build,'recording.prepare',req); rid=p['recordingId']; receipt['id']=rid
        receipt['ready']=d.wait_state(d.build,rid,('ready',),120)
        d.cli(d.build,'recording.overlay',{'id':rid,'visible':False}); time.sleep(6)
        d.cli(d.build,'recording.start',{'id':rid}); start=time.monotonic(); time.sleep(3)
        receipt['progress']=d.cli(d.build,'recording.inspect',{'id':rid}); receipt['sources']=d.recording_sources()
        time.sleep(max(0,60-(time.monotonic()-start)))
        receipt['stopped']=d.cli(d.build,'recording.stop',{'id':rid},timeout=60)
        assert receipt['stopped']['durationUs']>59_000_000, receipt['stopped']
        d.cli(d.build,'recording.cancel',{'id':rid}); d.close_cover(); d.cover=None
        src=run/'working'/f'{rid}.mkv'; receipt['working']={'file':str(src),'sha256':rr.sha256(src),'bytes':src.stat().st_size,'probe':probe(src)}
        # Gate the source with real covered desktop frames before any other data leaves the host.
        from PIL import Image
        from accept import check_frame
        for i,t in enumerate([2,30,58]):
            frame=run/'frames'/f'aac-working-{i}.png'; ff('-ss',str(t),'-i',src,'-frames:v','1',frame)
            with Image.open(frame) as im: rgb=im.convert('RGB')
            check_frame(run,frame,rgb)
    except Exception as e:
        receipt['errors'].append(str(e)); raise
    finally:
        try: d.stop_resident(d.build) if hasattr(d,'build') else None
        finally:
            try: d.close_cover()
            finally:
                try: receipt['soundCleanup']=d.close_microphone()
                finally:
                    if d.real_data is not None and d.real_data.exists(): d.real_data.rename(run/'real-data-putgd')
                    write(run/'capture.json',receipt)

def usage():
    r=resource.getrusage(resource.RUSAGE_CHILDREN); return (r.ru_utime,r.ru_stime)

def benchmark(run,candidate,stable):
    desktop_lock.refuse_while_quiet('AAC benchmark')
    c=json.loads((run/'capture.json').read_text()); assert not c['errors']; src=Path(c['working']['file']); assert rr.sha256(src)==c['working']['sha256']
    builds={label:rr.Build(label,img,run) for label,img in [('candidate',candidate),('stable',stable)]}
    receipt={'input':c['working'],'builds':{k:v.identity for k,v in builds.items()},'results':[],'loadStart':os.getloadavg(),'host':os.uname().nodename}
    out=run/'aac-results.json'
    for i in range(1,4):
        for label in (('candidate','stable') if i%2 else ('stable','candidate')):
            build=builds[label]; appdir=run/f'appdir-{label}'/'squashfs-root'; target=run/'out'/f'{label}-{i}.mp4'
            env=dict(os.environ,APPDIR=str(appdir)); env.pop('PUTGD_RECORD_DEBUG_LOG',None)
            command=[str(appdir/'usr/bin/putgd-record'),'--export',str(src),str(target),'--codec','h264']
            before=usage(); t=time.monotonic(); result=sp.run(command,env=env,capture_output=True,text=True,timeout=180); elapsed=time.monotonic()-t; after=usage()
            r={'label':label,'round':i,'wallSeconds':elapsed,'userCpuSeconds':after[0]-before[0],'systemCpuSeconds':after[1]-before[1], 'result':result.stdout.strip(),'returnCode':result.returncode,'stderrTail':result.stderr[-1500:],'output':str(target),'loadEnd':os.getloadavg()}
            receipt['results'].append(r); write(out,receipt); print(r['label'],r['round'],r['result'],f"elapsed={elapsed:.3f}s cpu={sum(after)-sum(before):.3f}s",flush=True)
            if result.returncode: raise RuntimeError(f'{label} export failed: {result.stderr[-300:]}')
    for r in receipt['results']:
        target=Path(r['output']); p=probe(target); r['probe']=p; r['sha256']=rr.sha256(target)
        a=sp.run(['ffmpeg','-hide_banner','-nostdin','-v','info','-xerror','-i',str(target),'-map','0:a:0','-af','volumedetect','-f','null','-'],capture_output=True,text=True,check=True)
        r['volumeDetect']={k:float(v) for k,v in re.findall(r'(mean_volume|max_volume):\s*(-?\d+(?:\.\d+)?) dB',a.stderr)}
        pcm=ff('-xerror','-i',target,'-map','0:a:0','-ac','1','-ar','48000','-f','f32le','-',capture_output=True).stdout
        audio=np.frombuffer(pcm,np.float32); parts=audio[:len(audio)//480*480].reshape(-1,480); t=np.arange(480)/48000
        r['decodedAudio']={'duration':len(audio)/48000,'rmsDb':float(20*np.log10(np.sqrt(np.mean(audio*audio)))),'median440':float(np.median(abs(parts@np.exp(-2j*np.pi*440*t))*2/480)),'peak1000':float(np.max(abs(parts@np.exp(-2j*np.pi*1000*t))*2/480))}
        write(out,receipt)
    receipt['summary']={}
    for label in builds:
        rows=[r for r in receipt['results'] if r['label']==label]
        receipt['summary'][label]={'medianWallSeconds':statistics.median(r['wallSeconds'] for r in rows),'medianCpuSeconds':statistics.median(r['userCpuSeconds']+r['systemCpuSeconds'] for r in rows),'encoders':sorted({r['result'].split()[0] for r in rows}),'meanVolumesDb':[r['volumeDetect'].get('mean_volume') for r in rows],'audioDurations':[r['decodedAudio']['duration'] for r in rows]}
    write(out,receipt)
    assert len({r['result'].split()[0] for r in receipt['results']})==1, 'encoder path differed'
    assert all(r['volumeDetect']['mean_volume']>-70 and abs(r['decodedAudio']['duration']-c['stopped']['durationUs']/1e6)<.2 for r in receipt['results'])
    print(json.dumps(receipt['summary'],indent=2))

if __name__=='__main__':
    mode=sys.argv[1]; run=Path(sys.argv[2]).resolve(); args=[Path(p).resolve() for p in sys.argv[3:]]
    (capture if mode=='capture' else benchmark)(run,*args)
