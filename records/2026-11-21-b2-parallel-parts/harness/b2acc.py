#!/usr/bin/env python3
"""#1792 lab helper (from #1782): B2 account checks for the isolated test prefix. Runs on the builder only.

The B2 key is read from ~/Documents/creds.txt into memory inside this process. It is never
printed, logged, written or passed in argv or the environment; `key-to-cli` hands it to
putgd-cli on stdin only.

  b2acc.py preflight                 bucket type, prefix empty, Backblaze upload networks
  b2acc.py check NAME LOCAL          the name's versions in the prefix vs the local file
  b2acc.py cleanup                   delete every version and unfinished large file in the prefix
  b2acc.py key-to-cli PROFILE REV    setup.storeCredentials for PROFILE through putgd-cli stdin
"""
import base64, hashlib, ipaddress, json, os, pathlib, re, socket, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
STATE = ROOT / 'state.json'
CREDS = pathlib.Path.home() / 'Documents/creds.txt'
API = 'https://api.backblazeb2.com/b2api/v3'


def master():
    # The bucket-scoped key block: "B2 keyID:", "B2 applicationKey:", "B2 bucket:".
    out = {}
    for line in CREDS.read_text().splitlines():
        m = re.match(r'^\s*([^:]+?)\s*:\s*(.*?)\s*$', line)
        if not m: continue
        k = m.group(1).lower().replace(' ', '')
        if k == 'b2keyid': out['id'] = m.group(2)
        elif k == 'b2applicationkey': out['key'] = m.group(2)
        elif k == 'b2bucket': out['bucket'] = m.group(2)
    if set(out) != {'id', 'key', 'bucket'}:
        sys.exit('B2 bucket-scoped key block not found')
    return out


def http(method, url, body=None, auth=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None: req.add_header('Content-Type', 'application/json')
    if auth: req.add_header('Authorization', auth)
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read() or b'{}')
        except Exception: return e.code, {}


class Account:
    def __init__(self):
        m = master()
        st, a = http('GET', API + '/b2_authorize_account', auth='Basic ' + base64.b64encode(f"{m['id']}:{m['key']}".encode()).decode())
        m.clear()
        if st != 200: sys.exit(f'authorize failed: {st} {a.get("code")}')
        s = a['apiInfo']['storageApi']
        self.api, self.token, self.account, self.download = s['apiUrl'], a['authorizationToken'], a['accountId'], s['downloadUrl']
        allowed = s.get('allowed', s)
        buckets = allowed.get('buckets') or ([{'id': allowed.get('bucketId'), 'name': allowed.get('bucketName')}] if allowed.get('bucketId') else [])
        self.bucket = buckets[0] if len(buckets) == 1 else None
    def call(self, name, body):
        st, r = http('POST', f'{self.api}/b2api/v3/{name}', body, auth=self.token)
        if st != 200: sys.exit(f'{name} failed: {st} {r.get("code")}')
        return r


def state():
    return json.loads(STATE.read_text())


def bucket(acct):
    s = state()
    if not acct.bucket: sys.exit('expected a key restricted to one bucket')
    st, r = http('POST', f'{acct.api}/b2api/v3/b2_list_buckets', {'accountId': acct.account, 'bucketName': acct.bucket['name']}, auth=acct.token)
    kind = r['buckets'][0]['bucketType'] if st == 200 and r.get('buckets') else 'allPrivate'
    return {'bucketId': acct.bucket['id'], 'bucketName': acct.bucket['name'], 'bucketType': kind}, s['prefix']


def sha1_of(acct, file_id):
    req = urllib.request.Request(f'{acct.download}/b2api/v3/b2_download_file_by_id?fileId={urllib.parse.quote(file_id)}')
    req.add_header('Authorization', acct.token)
    h, n = hashlib.sha1(), 0
    try:
        r = urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as e:
        try: code = json.loads(e.read() or b'{}').get('code')
        except Exception: code = None
        return None, None, f'{e.code} {code}'
    with r:
        while True:
            chunk = r.read(1 << 20)
            if not chunk: break
            h.update(chunk); n += len(chunk)
    return h.hexdigest(), n, None


def versions(acct, bid, prefix):
    out, start, sid = [], None, None
    while True:
        body = {'bucketId': bid, 'prefix': prefix, 'maxFileCount': 1000}
        if start: body.update(startFileName=start, startFileId=sid)
        r = acct.call('b2_list_file_versions', body)
        out += r['files']
        if not r.get('nextFileName'): return out
        start, sid = r['nextFileName'], r['nextFileId']


def main():
    action = sys.argv[1]
    acct = Account()
    if action == 'key-to-cli':
        # The CLI refuses keys by design; this talks to the private resident's socket directly,
        # as the Settings window would hand them over. The key stays in this process.
        profile, rev, sock = sys.argv[2], sys.argv[3], sys.argv[4]
        m = master()
        request = json.dumps({'schemaVersion': 1, 'requestId': 'b1792-store', 'session': sock, 'method': 'setup.storeCredentials',
                              'params': {'profileId': profile, 'expectedRevision': rev, 'credentials': {'accessKey': m['id'], 'secretKey': m['key']}}}).encode() + b'\n'
        m.clear()
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
            c.settimeout(30); c.connect(sock); c.sendall(request); request = b''
            reply = b''
            while not reply.endswith(b'\n'):
                chunk = c.recv(65536)
                if not chunk: break
                reply += chunk
        value = json.loads(reply or b'{}')
        print(json.dumps({'ok': value.get('ok'), 'setupId': (value.get('result') or {}).get('setupId'), 'error': (value.get('error') or {}).get('code')}))
        return
    if action == 'api':
        host = urllib.parse.urlsplit(acct.api).hostname
        print(sorted({i[4][0] for i in socket.getaddrinfo(host, 443, socket.AF_INET)})[0])
        return
    b, prefix = bucket(acct)
    assert re.fullmatch(r'acceptance/i1792-[0-9a-f]{12}/', prefix), prefix
    if action == 'preflight':
        files = versions(acct, b['bucketId'], prefix)
        nets = set()
        for _ in range(6):
            host = urllib.parse.urlsplit(acct.call('b2_get_upload_url', {'bucketId': b['bucketId']})['uploadUrl']).hostname
            for info in socket.getaddrinfo(host, 443, socket.AF_INET):
                nets.add(str(ipaddress.ip_network(info[4][0] + '/16', strict=False)))
        print(json.dumps({'bucketType': b['bucketType'], 'prefixEmpty': not files, 'uploadNetworks': sorted(nets)}))
        s = state(); s['bucketName'] = b['bucketName']; s['bucketType'] = b['bucketType']; STATE.write_text(json.dumps(s))
    elif action == 'check':
        name, local = prefix + sys.argv[2], pathlib.Path(sys.argv[3])
        data = local.read_bytes()
        found = [f for f in versions(acct, b['bucketId'], prefix) if f['fileName'] == name]
        unfinished = acct.call('b2_list_unfinished_large_files', {'bucketId': b['bucketId'], 'namePrefix': prefix})['files']
        rows = []
        for f in found:
            info = f.get('fileInfo', {})
            sha1 = f.get('contentSha1') or ''
            # A large file has no stored SHA-1: download it and hash what B2 serves.
            served = sha1_of(acct, f['fileId']) if f['action'] == 'upload' else (None, None, None)
            rows.append({'action': f['action'], 'bytesMatch': f.get('contentLength') == len(data),
                         'downloadedSha1Match': served[0] == hashlib.sha1(data).hexdigest() if served[0] else None,
                         'downloadedBytesMatch': served[1] == len(data) if served[1] is not None else None,
                         'downloadRefused': served[2], 'fileId': f['fileId'],
                         'sha1Match': sha1 == hashlib.sha1(data).hexdigest() if sha1 and sha1 != 'none' else None,
                         'putgdSha256Match': urllib.parse.unquote(info.get('putgd-sha256', '')) == hashlib.sha256(data).hexdigest(),
                         'large': sha1 in ('', 'none') or 'large_file_sha1' in info})
        print(json.dumps({'versions': rows, 'unfinishedLargeFiles': len(unfinished)}))
    elif action == 'cleanup':
        files = versions(acct, b['bucketId'], prefix)
        for f in files:
            assert f['fileName'].startswith(prefix)
            if f['action'] == 'start':
                continue
            acct.call('b2_delete_file_version', {'fileName': f['fileName'], 'fileId': f['fileId']})
        unfinished = acct.call('b2_list_unfinished_large_files', {'bucketId': b['bucketId'], 'namePrefix': prefix})['files']
        for f in unfinished:
            acct.call('b2_cancel_large_file', {'fileId': f['fileId']})
        after = versions(acct, b['bucketId'], prefix)
        left = acct.call('b2_list_unfinished_large_files', {'bucketId': b['bucketId'], 'namePrefix': prefix})['files']
        print(json.dumps({'versionsDeleted': len([f for f in files if f['action'] != 'start']), 'largeCancelled': len(unfinished),
                          'prefixEmpty': not after and not left}))


main()
