from pathlib import Path
import shutil
b=Path('/tmp/p4a');e=b/'2026-11-12-proton-chosen-connection-acceptance-round4';p=e/'README.md';s=p.read_text();s=s.replace('Fedora returned `clipboard_unavailable` on 11 completed upload operations (batch-3, text-small, after-cancel and eight individual paired operations).', 'Fedora logged `clipboard_unavailable` on all 24 completed upload operations. The CLI terminal snapshots carried that error for 11 operations; the full app log contains 24 clipboard failure events. These are different observation points. Asterisks in the time table mark only the CLI snapshots with that error.')
s += '\nPublication correction: the first evidence commit described 11 clipboard errors from terminal CLI snapshots. Full-log counting showed 24 distinct completed operations with a clipboard warning. This README was amended to state both counts; all original result JSON and app logs are unchanged.\n'
p.write_text(s);shutil.copy2(b/'correct4.py',e/'correct4.py')
