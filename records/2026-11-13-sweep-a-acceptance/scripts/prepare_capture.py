from pathlib import Path
src=Path('/tmp/sa1113/checks.py').read_text()
src=src[:src.index('build = cli(')]
src=src.replace("ROOT = os.path.expanduser('~/work/i1363')", "ROOT = os.environ['SWEEP_ROOT']")
src=src.replace("WORK = tempfile.mkdtemp(prefix='p1363-checks-')", "WORK = os.path.join(RUN, 'acceptance'); os.makedirs(WORK, mode=0o700, exist_ok=True)")
src=src.replace("    return r.get('result', r) if isinstance(r, dict) else r", "    with open(os.path.join(WORK, 'session.jsonl'), 'a') as f: f.write(json.dumps({'method': method, 'params': params, 'reply': r}) + '\\n')\n    return r.get('result', r) if isinstance(r, dict) else r")
src+='''
assert cli('diagnostics')['build']['gitTree'] == '1148ea1108a4f28a749607cf4a8ee8cbbdd90fc7'
doc=cli('settings.get')
cli('settings.patch', {'patch': {'archive': {'keepUploads': True}, 'preferences': {'notifications': False, 'regionSelectionMode': 'live'}}, 'expectedRevision': doc['metadata']['observedRevision']})
time.sleep(8)
def compare(name, action, box, selection=None, delay=0):
    move(20,740); time.sleep(.5)
    full=invoke('desktop'); reference=fetch(full['path']) if full['path'] else None
    op,_=start(action,delay)
    if selection:
        time.sleep(2); drag(*selection)
    r=wait(op)
    image=fetch(r['path']) if r['path'] else None
    expected=reference.crop(box) if reference else None
    difference=differs(image,expected) if image and expected and image.size==expected.size else None
    ok=r['state']=='completed' and difference is not None and difference<1
    row(name,ok,json.dumps({'operationId':op,'state':r['state'],'error':r['code'],'dimensions':image.size if image else None,'meanAbsoluteDifference':difference}))
    for head in (0,1): dump(head).save(os.path.join(WORK,name.replace(' ','-')+'-head%d.png'%head))
    if image: image.save(os.path.join(WORK,name.replace(' ','-')+'-result.png'))
    return ok
compare('region-one-monitor','region',(300,300,600,500),(300,300,600,500))
compare('region-two-monitors','region',(1100,300,1450,500),(1100,300,1450,500))
compare('repeat-region','repeat',(1100,300,1450,500))
compare('desktop','desktop',(0,0,2304,800))
move(1700,500)
# Monitor pointer is placed immediately before invoking by a separate routine.
full=invoke('desktop'); reference=fetch(full['path']); move(1700,500); r=invoke('monitor')
image=fetch(r['path']) if r['path'] else None
row('monitor-under-pointer',image is not None and image.size==(1024,768) and differs(image,reference.crop((1280,0,2304,768)))<1,json.dumps(r))
compare('live-region-delay-3','region',(300,300,600,500),(300,300,600,500),3)
print('# %d failed'%failed[0],flush=True)
sys.exit(1 if failed[0] else 0)
'''
Path('/tmp/sa1113/capture_acceptance.py').write_text(src)
