"""Drive the put.gd MCP helper over stdio: patch kinds, capture (report mode), get_operation, decide_upload."""
import asyncio, json, sys, time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

root, kinds = sys.argv[1], json.loads(sys.argv[2])

def body(result):
    for c in result.content:
        if getattr(c, 'text', None):
            try:
                return json.loads(c.text)
            except ValueError:
                return c.text
    return getattr(result, 'structuredContent', None)

async def main():
    params = StdioServerParameters(command=f'{root}/m/mcp/.venv/bin/putgd-mcp', args=['--cli', '/usr/bin/putgd-cli', '--socket', f'{root}/r/putgd/session.sock'])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            out = {}
            info = body(await s.call_tool('inspect', {}))
            def find(d):
                if isinstance(d, dict):
                    if 'observedRevision' in d: return d['observedRevision']
                    for v in d.values():
                        r = find(v)
                        if r: return r
            rev = find(info)
            out['revisionFromInspect'] = bool(rev)
            out['patch'] = body(await s.call_tool('patch_configuration', {'patch': {'preferences': {'sensitiveTextCheck': {'enabled': True, 'kinds': kinds}}}, 'expected_revision': rev}))
            cap = body(await s.call_tool('perform_action', {'action': 'monitor'}))
            out['capture'] = cap
            oid = cap.get('result', cap).get('operationId')
            for _ in range(600):
                op = body(await s.call_tool('get_operation', {'id': oid}))
                o = op.get('result', op)
                if o.get('phase') == 'sensitive_text_found' or o.get('state') in ('completed', 'failed', 'cancelled'):
                    break
                await asyncio.sleep(.2)
            out['firstStop'] = {'state': o.get('state'), 'phase': o.get('phase'), 'sensitive': o.get('sensitive')}
            if o.get('phase') == 'sensitive_text_found':
                out['decide'] = body(await s.call_tool('decide_upload', {'id': oid, 'choice': 'upload'}))
                for _ in range(600):
                    o = body(await s.call_tool('get_operation', {'id': oid})); o = o.get('result', o)
                    if o.get('state') in ('completed', 'failed', 'cancelled'):
                        break
                    await asyncio.sleep(.2)
            out['final'] = {'id': oid, 'state': o.get('state'), 'sensitive': o.get('sensitive')}
            print(json.dumps(out))

asyncio.run(main())
