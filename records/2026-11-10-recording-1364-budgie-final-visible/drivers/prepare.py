from pathlib import Path
import re
s=Path('/tmp/b1364-new/record_run_new.py').read_text()
s=re.sub(r'\b(clip|saved)\.unlink\([^)]*\)',r'retain_private(\1)',s)
s=s.replace("entry['destroyed'] = True","entry['retainedPrivately'] = True").replace("result['clips'][kind]['destroyed'] = True","result['clips'][kind]['retainedPrivately'] = True").replace('the clips were deleted','the clips were retained privately').replace('deleted unopened','retained privately')
s=s.replace('import shutil\n',"import shutil\n\ndef retain_private(path):\n    # This final disposable-guest cell must not destroy rejected evidence.\n    pass\n")
assert '.unlink('not in s
Path('/tmp/b1364-visible/record_run_visible.py').write_text(s)
s=Path('/tmp/b1364/cover_player.py').read_text();s=re.sub(r'\bpath\.unlink\([^)]*\)',r'pass # retain privately; guard judgement unchanged',s);s=s.replace('deleted=True','deleted=False, retainedPrivately=True');assert '.unlink('not in s
Path('/tmp/b1364-visible/cover_player.py').write_text(s)
