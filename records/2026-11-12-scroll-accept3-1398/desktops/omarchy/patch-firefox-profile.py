from pathlib import Path
import json
P=Path('/home/lab/work/s3a');f=P/'browsercases.py';s=f.read_text();(P/'browsercases-before-tou.py').write_text(s)
needle='user_pref("browser.aboutwelcome.enabled",false);'
assert needle in s
s=s.replace(needle,needle+'user_pref("termsofuse.acceptedVersion",999);user_pref("termsofuse.bypassNotification",true);');f.write_text(s)
(P/'firefox-profile-correction.json').write_text(json.dumps({'reason':'Firefox first-run Terms modal blocked wheel input. Disposable test profile explicitly skips it using installed Firefox prefs; no real browser profile modified.','installedSource':'/usr/lib/firefox/browser/omni.ja defaults/preferences/firefox.js and modules/policies/Policies.sys.mjs (SkipTermsOfUse uses acceptedVersion999)','preferences':{'termsofuse.acceptedVersion':999,'termsofuse.bypassNotification':True}},indent=2))
