import json,statistics
from pathlib import Path
lines=['\x1b[1;33m#1380: PHYSICAL Cinnamon/X11 compatibility check - Qt 6.4.2\x1b[0m','Head 04ee694dd2523652c06cc8f78560f1bd92e81981','m74 / Mint 22.3 / Cinnamon 6.6.4 / private roots / source build','capture_preparation_x11: PASS (7.93 s), unchanged strict assertions','Shortcut maps selector: PASS; drag captures 400x250 PNG: PASS','Escape cancels without another output file: PASS','Warm-up PID3909215 XID0x4c00006: 160x160, Map State IsUnMapped','Separate 1x1 mapped cursor child is embedded in the native selector.','','Mapping: 60 samples/build, 2 opposite-order batches; 5 warmups/batch','                       hotkey->map mean/worst    helper-start upper mean/worst']
values={}
for label in ('nightly','fixed'):
 rows=[]
 for run in ('m17','m18'):rows+=json.loads(Path(f'/tmp/{run}/{label}/latency.json').read_text())['samples']
 a=[r['mapMs'] for r in rows];b=[r['windowWitnesses'][0]['helperStartToMapUpperMs'] for r in rows];values[label]=statistics.mean(b)
 lines.append(f'{label:12s}           {statistics.mean(a):6.2f} / {max(a):6.2f} ms         {statistics.mean(b):6.2f} / {max(b):6.2f} ms')
lines+=['','Helper start uses /proc startTicks: 10 ms timestamp quantization.','Each actual helper-start->map time is in [reported upper-10, upper].',f'Observed mean upper-bound delta: +{values["fixed"]-values["nightly"]:.2f} ms; mean intervals overlap.','No reliable sub-10-ms conclusion; this does not prove zero difference.','XCURSOR_RESIZED=1 exercises the changed fallback/warm-up path.','Normal static cursor seeding skips warm-up on Qt 6.4.2.','All captures local/synthetic; no user destination or settings touched.']
Path('/tmp/pg-m74-results.txt').write_text('\n'.join(lines)+'\n')
