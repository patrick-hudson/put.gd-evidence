import datetime, hashlib, json, os, selectors, signal, subprocess, sys, time
from pathlib import Path
root = Path.home()/"work/ocr-integration-bcb-artifacts"
sys.path.insert(0,str(root/"audit-source/tools/releases"))
from portable_appimage import audit_ocr_runtime
import appimage_notices
image = next((root/"integration-appimage").glob("*.AppImage"))
image.chmod(0o755)
expected=json.loads((root/"integration-appimage/build-info.json").read_text())
receipt={"schemaVersion":1,"run":43380438975,"expectedCommit":"bcb868f9ac5b50967976656ed306858f5d8ae72f","host":"k72","utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"image":image.name,"imageBytes":image.stat().st_size,"imageSha256":hashlib.file_digest(image.open('rb'),'sha256').hexdigest(),"environment":{},"mountEnvironment":{"PATH":"/usr/bin:/bin"},"scope":"Mounted exact CI AppImage; helper identity and ELF loader resolution only; no desktop/session launched"}
log=(root/"mounted-appimage-stderr.log").open('w')
proc=subprocess.Popen([str(image),"--appimage-mount"],stdout=subprocess.PIPE,stderr=log,text=True,env={"PATH":"/usr/bin:/bin"})
mount=None
try:
    receipt["mountPid"]=proc.pid
    selector=selectors.DefaultSelector(); selector.register(proc.stdout,selectors.EVENT_READ)
    if not selector.select(30): raise RuntimeError("FUSE mount did not report its path")
    mount=Path(proc.stdout.readline().strip()).resolve()
    selector.close()
    if not str(mount).startswith('/tmp/.mount_') or not mount.is_mount(): raise RuntimeError(f"Not an AppImage FUSE mount: {mount}")
    receipt["fuseMount"]=str(mount)
    receipt["mountInfo"]=[s for s in Path('/proc/self/mountinfo').read_text().splitlines() if str(mount) in s]
    helper=mount/'usr/bin/putgd-ocr'
    result=subprocess.run([str(helper),'--version-json'],check=True,capture_output=True,text=True,env={},timeout=30)
    identity=json.loads(result.stdout)
    for key in ('gitCommit','gitTree','version','commitCount'):
        if identity[key]!=expected[key]: raise ValueError(f"identity mismatch: {key}")
    if identity['gitCommit']!=receipt['expectedCommit']: raise ValueError('Wrong integration commit')
    receipt['helperIdentity']=identity
    receipt['ocr']=audit_ocr_runtime(mount)
    receipt['notices']=appimage_notices.audit(mount)
    receipt['helperRunpath']=subprocess.run(['readelf','-d',str(helper)],check=True,capture_output=True,text=True,env={}).stdout
    receipt['lddEmptyEnvironment']=subprocess.run(['ldd',str(helper)],check=True,capture_output=True,text=True,env={}).stdout
    receipt['status']='passed'
finally:
    proc.send_signal(signal.SIGINT) if proc.poll() is None else None
    try: proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.terminate()
        try: proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill(); proc.wait(timeout=10)
    log.close()
    receipt['mountProcessExit']=proc.returncode
    deadline=time.monotonic()+5
    while mount is not None and mount.is_mount() and time.monotonic()<deadline:
        time.sleep(.05)
    if mount is not None and str(mount).startswith('/tmp/.mount_') and mount.is_mount():
        subprocess.run(['/usr/bin/fusermount','-u',str(mount)],check=True,timeout=15)
        receipt['unmountCommand']=['/usr/bin/fusermount','-u',str(mount)]
    receipt['unmounted']=mount is not None and not mount.is_mount()
    (root/'mounted-appimage-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if mount is not None and mount.is_mount(): raise RuntimeError('Own FUSE mount still present')
print(json.dumps({k:receipt[k] for k in ('imageBytes','imageSha256','status','unmounted')}))
