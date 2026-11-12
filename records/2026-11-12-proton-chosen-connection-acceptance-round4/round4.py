#!/usr/bin/env python3
# Round 3 capture/state/failure instrumentation reused; no control or sequential captures.
import round3 as r
import proton_accept as p
import sys,json
p.helpers_gone=r.orig_gone
originals=['file-64k','file-1m','file-8m','batch-3','text-small','back-to-back','desktop-now','desktop-delay3','desktop-delay3-again','monitor-delay3','cancel-countdown','after-cancel','history-picture','link-answers']
def run(app,tests,only):
    results=r.run(app,tests,set(originals))
    pairs=[dict(pair=1,orderKiB=[512,64],**next(x for x in results if x['name']=='back-to-back'))]
    if pairs[0].get('helperGoneAfter') is None:raise p.Failure('Helper remains; extra pairs refused')
    for i in range(2,10):
        swapped=i>=6
        random=p.os.urandom
        if swapped:
            p.os.urandom=lambda n:random(65536 if n==524288 else 524288 if n==65536 else n)
        try: rows=r.run(app,tests,{'back-to-back'})
        finally:p.os.urandom=random
        row=rows[0];row['name']=f'back-to-back-{i}'
        results+=rows
        pairs.append(dict(pair=i,orderKiB=[64,512] if swapped else [512,64],**row))
        (app.work/'pairs.json').write_text(json.dumps(pairs,indent=2))
        if row.get('helperGoneAfter') is None:raise p.Failure('Helper remains; next pair refused')
    results+=r.run(app,tests,{'revoke-all'})
    return results
p.run=run
if __name__=='__main__':
    # --only prevents round3 start adapter from scheduling a nightly control.
    sys.argv+=['--only']+originals+['revoke-all']
    sys.exit(p.main())
