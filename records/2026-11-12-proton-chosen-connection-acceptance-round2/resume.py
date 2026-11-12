import round2 as r
import proton_accept as p
import json,sys
from pathlib import Path
r.controlled=True
original_mkdir=Path.mkdir
work=Path('pr').resolve()
def mkdir(self,*a,**kw):
    if self.resolve()==work or (self.resolve().is_relative_to(work/'profile') and self.is_dir()): return
    return original_mkdir(self,*a,**kw)
Path.mkdir=mkdir
(work/'results.json').rename(work/'interrupted-results.json')
(work/'resident.log').rename(work/'resident-before-control.log')
p.configure=lambda app: next(x for x in json.loads(p.LAB_CONFIG.read_text())['profiles'] if x['id']==p.PROFILE_ID)['settings']['folderName']
def run(app,tests,only):
    names={'batch-3','text-small','back-to-back','desktop-now','desktop-delay3','desktop-delay3-again','monitor-delay3','cancel-countdown','after-cancel','history-picture','revoke-all'}
    results=r.orig_run(app,tests,names)
    for n in range(1,4):
        extra=r.orig_run(app,tests,{'desktop-now'})
        for x in extra:x['name']=f'sequential-desktop-{n}'
        results+=extra
    extra=r.orig_run(app,tests,{'revoke-all'})
    for x in extra:x['name']='revoke-additions'
    results+=extra
    rows=app.need('history.list',{'limit':100,'offset':0}).get('records',[])
    remaining=[x.get('id') for x in rows if x.get('linkAvailable')]
    (work/'revocation-verification.json').write_text(json.dumps({'rows':len(rows),'remainingLinkHistoryIds':remaining,'allRevoked':not remaining}))
    return results
p.run=run
sys.exit(p.main())
