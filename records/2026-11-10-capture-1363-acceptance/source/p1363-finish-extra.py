import json
from pathlib import Path
E=Path.home()/'work/i1363/work/acceptance-1363/ac5';read=lambda n:json.loads((E/(n+'.json')).read_text())
w=read('warmup-results');assert w['passed'];assert w['diagnostics']['build']['gitTree']=='1e2d35a411dc2f281b3c3414c87503a62476eba8'
m=read('mcp-live');assert len(m)==7 and all(x['state']=='completed' for x in m)
assert len(read('mcp-invalid-delays'))==5 and len(read('mcp-invalid-delay-types'))==2 and read('mcp-invalid-cli-count')['passed']
report={'completed':True,'passed':True,'scope':'Extra Cinnamon AppImage Qt>=6.11 X11 warm-up intersection and installed-resident MCP new-action cases; full shared Settings cases belong to native DEB ac4','build':w['diagnostics']['build'],'qt':w['diagnostics'].get('qtVersion'),'warmup':{'plainShortcutAfterDragSeconds':w['plainShortcutAfterDragSeconds'],'delayedAfterDragSeconds':w['delayedAfterDragSeconds'],'loadedHelperQt':w['loadedHelperQt']},'mcpValid':7,'mcpInvalidWithoutCli':7,'mcpOperationIds':[r['id'] for r in m]}
(E/'gui-results.json').write_text(json.dumps(report,indent=2));(E/'gui-finished').touch();print(json.dumps(report,indent=2))
