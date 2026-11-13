from pathlib import Path
import collections,datetime,hashlib,json,subprocess
r=Path.home()/'work/ocr-pkg-1438-scan'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
bindings=json.loads((r/'integration-package-bindings.json').read_text())
sboms=json.loads((r/'integration-sboms/sbom-receipts.json').read_text())['sboms']
report=json.loads((r/'stable-policy-bcb/vulnerability-report.json').read_text())
assert bindings['commit']=='bcb868f9ac5b50967976656ed306858f5d8ae72f' and len(sboms)==6
assert report['channel']=='stable'
for label,s in sboms.items():
 assert s['packageSha256']==bindings['packages'][label]['sha256']
 assert sha(r/'integration-sboms'/s['file'])==s['sha256']
assert sha(r/'candidate-integration.AppImage')==sboms['appimage']['packageSha256']
flagged=[x for x in report['findings'] if x['status'].startswith(('blocking','flagged'))]
assert not flagged
new=[x for x in report['findings'] if any(w in x['component'].lower() for w in ('tesser','lepton','zxing','zueci','tessdata','qrcodegen'))]
assert not new
policy=r/'integration-source/packaging/sbom/policy.json'
assert sha(policy)=='f759c346c86830bf44db9f93923525058a7fc7f33584b1f7df7c253a09b7ffc3'
receipt={'run':bindings['run'],'commit':bindings['commit'],'host':'d69','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scanCommand':'GRYPE_DB_CACHE_DIR="$PWD/db-cache" python3 integration-source/tools/releases/sbom.py scan --sboms integration-sboms --grype "$PWD/scan-tools/grype" --output stable-policy-bcb --database integration-current-db.json --release-tag v26.1113.4805 --summary stable-integration-summary.md','observedCommandExit':0,'channel':report['channel'],'mode':'STABLE policy rehearsal only; no release tag created or publication performed','database':report['database'],'policySha256':sha(policy),'policyAcceptancesAdded':[],'findings':len(report['findings']),'flagged':len(flagged),'newOcrQrComponentFindings':new,'statusCounts':dict(collections.Counter(x['status'] for x in report['findings'])),'severityCounts':dict(collections.Counter(x['severity'] for x in report['findings'])),'grypeVersion':json.loads(subprocess.check_output([str(r/'scan-tools/grype'),'version','-o','json'],text=True)),'toolBinarySha256':{name:sha(r/'scan-tools'/name) for name in ('grype','syft')},'packageBindings':bindings['packages'],'reportSha256':sha(r/'stable-policy-bcb/vulnerability-report.json'),'scope':'All six package SBOMs, each independently bound to the exact integration CI installer SHA-256; native distro libraries remain distribution managed and are not bundled-code components'}
(r/'stable-integration-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('commit','findings','flagged','policyAcceptancesAdded','severityCounts')},indent=2))
