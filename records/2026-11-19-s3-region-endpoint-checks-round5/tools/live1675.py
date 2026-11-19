#!/usr/bin/env python3
"""Live check for #1675 and #1676 against Cloudflare R2 and AWS S3.

  python3 -I live1675.py --tree ~/work/w1675 --build DIR --run /tmp/i1675/X --out FILE.json [--cases ...]

Runs an isolated resident (af.Resident: private XDG roots, offscreen, PUTGD_STARTED_FOR_UPLOAD=1, session credentials)
under the caller's dbus-run-session. Credentials are read from ~/Documents/creds.txt in memory only and go to the resident
through its session socket; nothing printed or written carries them. Account ID and bucket are replaced by <acct> and
<bucket> in everything written. What the cases upload lands under i1675-test/ (or, for an Endpoint with the bucket on the
end, under <bucket>/i1675-test/), and every key under both is deleted at the end and checked gone.
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--tree', required=True)
parser.add_argument('--build', required=True)
parser.add_argument('--run', required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--cases', default='r2-region-label,r2-endpoint-bucket,r2-correct,aws-correct')
options = parser.parse_args()
sys.path.insert(0, str(Path(options.tree) / 'tools/lab'))
import action_fuzz as af  # noqa: E402
import s3_differential as diff  # noqa: E402

PREFIX = 'i1675-test/'
creds = diff.cloud_credentials()
r2_key, r2_secret, r2_endpoint = creds['r2']
r2_bucket = os.environ.get('S3DIFF_R2_BUCKET') or diff.r2_bucket(r2_key, r2_secret, r2_endpoint)
account = urllib.parse.urlsplit(r2_endpoint).hostname.split('.')[0]
aws_key, aws_secret = creds['aws2']
secrets = [r2_key, r2_secret, aws_key, aws_secret]


def redact(value):
    text = json.dumps(value)
    for secret in secrets:
        if secret in text:
            raise SystemExit('a credential reached a result; nothing written')
    return json.loads(text.replace(account, '<acct>').replace(r2_bucket, '<bucket>'))


def settings(endpoint, bucket, region, prefix, link_mode='presigned'):
    return {'endpoint': endpoint, 'bucket': bucket, 'region': region, 'objectPrefix': prefix, 'aclMode': 'omit', 'addressing': 'auto',
            'publicUrlBase': None, 'requestTimeoutMs': 30000, 'connectTimeoutMs': 5000, 'storageClass': 'STANDARD',
            'lowSpeedBytesPerSecond': 1, 'lowSpeedTimeSeconds': 30, 'linkMode': link_mode, 'linkValidityDays': 1}


CASES = {
    # What the reporter typed: the location label the Cloudflare dashboard shows.
    'r2-region-label': ('r2', settings(r2_endpoint, r2_bucket, 'Western North America (WNAM)', PREFIX)),
    # The same on a host that isn't Cloudflare R2: AWS signs with Region.
    'aws-region-label': ('aws', settings('https://s3.us-east-2.amazonaws.com', 'put.gd', 'Western North America (WNAM)', 'acceptance/i1675-test/')),
    # The bucket's full S3 URL pasted into Endpoint, Bucket filled too.
    'r2-endpoint-bucket': ('r2', settings(r2_endpoint.rstrip('/') + '/' + r2_bucket, r2_bucket, 'auto', PREFIX)),
    # The profile an earlier run left in this run's configuration, tested as it is.
    'saved-earlier': ('r2', None),
    # A first-time R2 user who leaves Region empty.
    'r2-region-blank': ('r2', settings(r2_endpoint, r2_bucket, '', PREFIX)),
    # The same endpoint typed with an uppercase scheme and host.
    'r2-upper-endpoint': ('r2', settings(r2_endpoint.replace('https://', 'HTTPS://').upper().replace('HTTPS://', 'HTTPS://'), r2_bucket, 'auto', PREFIX)),
    # An encoded separator in the path: the message must quote it as typed.
    'r2-endpoint-encoded': ('r2', settings(r2_endpoint.rstrip('/') + '/' + r2_bucket + '%2Ffolder/', r2_bucket, 'auto', PREFIX)),
    'r2-correct': ('r2', settings(r2_endpoint, r2_bucket, 'auto', PREFIX)),
    'aws-correct': ('aws', settings('https://s3.us-east-2.amazonaws.com', 'put.gd', 'us-east-2', 'acceptance/i1675-test/')),
}

run = Path(options.run)
(run / 'logs').mkdir(parents=True, exist_ok=True)
resident = af.Resident(run, options.build)
results = {'build': options.build, 'cases': {}}
try:
    resident.start()
    results['version'] = (resident.call('capabilities') or {}).get('version') or (resident.call('diagnostics') or {}).get('version')
    template = json.loads(json.dumps(resident.call('settings.developmentTemplate')['document']['profiles'][0]))
    for name in options.cases.split(','):
        service, profile_settings = CASES[name]
        record = {}
        current = resident.call('settings.get', raw=True)
        record['loaded'] = {'validation': (current.get('result') or {}).get('metadata', {}).get('validation'),
                            'settings': [p.get('settings') for p in (current.get('result') or {}).get('document', {}).get('profiles', [])]}
        current = current['result']
        if profile_settings is None:
            saved = {'ok': True}
        else:
            document = current['document']
            profile = dict(template, id='i1675', label='i1675 ' + name, credentials={'mode': 'session', 'reference': None}, settings=profile_settings)
            document['profiles'] = [profile]
            saved = resident.call('settings.save', {'document': document, 'expectedRevision': current['metadata']['observedRevision']}, raw=True)
        record['save'] = {'ok': bool(saved.get('ok')), 'error': saved.get('error')}
        if saved.get('ok'):
            access, secret = (r2_key, r2_secret) if service == 'r2' else (aws_key, aws_secret)
            stored = resident.call('setup.storeCredentials', {'profileId': 'i1675', 'expectedRevision': resident.call('settings.get')['metadata']['observedRevision'],
                                                               'credentials': {'accessKey': access, 'secretKey': secret}}, raw=True)
            setup = (stored.get('result') or {}).get('setupId')
            end = time.monotonic() + 30
            while setup and time.monotonic() < end and (resident.call('setup.inspect', {'id': setup}) or {}).get('state') == 'running':
                time.sleep(0.2)
            tested = resident.call('setup.testDestination', {'profileId': 'i1675', 'expectedRevision': resident.call('settings.get')['metadata']['observedRevision']}, raw=True)
            setup = (tested.get('result') or {}).get('setupId')
            state = None
            end = time.monotonic() + 180
            while setup and time.monotonic() < end:
                state = resident.call('setup.inspect', {'id': setup})
                if state.get('state') != 'running':
                    break
                time.sleep(0.5)
            record['test'] = {'accepted': bool(tested.get('ok')), 'startError': tested.get('error'),
                              'state': (state or {}).get('state'), 'error': (state or {}).get('error'), 'result': (state or {}).get('result')}
        results['cases'][name] = record
        print(name, json.dumps(redact(record))[:600], flush=True)
finally:
    try:
        resident.quit()
    except Exception:  # noqa: BLE001
        pass
    # Whatever the cases left, under the prefix or under the doubled bucket path.
    r2 = diff.CloudTarget('r2', r2_endpoint, 'auto', r2_bucket, r2_key, r2_secret, PREFIX)
    aws = diff.CloudTarget('aws', 'https://s3.us-east-2.amazonaws.com', 'us-east-2', 'put.gd', aws_key, aws_secret, 'acceptance/i1675-test/')
    cleanup = {}
    for label, target, prefix in (('r2', r2, PREFIX), ('r2-doubled', r2, r2_bucket + '/' + PREFIX), ('aws', aws, 'acceptance/i1675-test/')):
        try:
            left = [key for key, _size, _etag in target.raw_keys(prefix)]
            target.cleanup(prefix)
            cleanup[label] = {'found': len(left), 'removed': True}
        except Exception as error:  # noqa: BLE001
            cleanup[label] = {'error': str(error)[:300]}
    results['cleanup'] = cleanup
    print('cleanup', json.dumps(redact(cleanup)), flush=True)
    Path(options.out).write_text(json.dumps(redact(results), indent=1))
