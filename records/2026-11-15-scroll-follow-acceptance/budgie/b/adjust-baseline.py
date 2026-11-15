import accept as A,json,subprocess
P=A.P
assert not subprocess.run(['pgrep','-x','putgd-record'],capture_output=True,text=True).stdout.strip(),'a helper already owns a settings snapshot; wait for its cleanup before adjusting'
s=A.rpc('settings.get');d=s['document'];before=d['preferences']['scrollCaptureFromTop'];d['preferences']['scrollCaptureFromTop']=False
A.rpc('settings.save',{'document':d,'expectedRevision':s['metadata']['observedRevision']});A.rpc('settings.reload')
(P/'scroll-from-top-comparison-setting.json').write_text(json.dumps({'baselineDefault':before,'candidateSetting':False,'testedBaselineSetting':False,'reason':'Compare direct capture at the same nominal 2-second start. The candidate development template has From top false and nightly has true. Only the isolated baseline configuration changed.'},indent=1))
print('Baseline From top false matches candidate',flush=True)
