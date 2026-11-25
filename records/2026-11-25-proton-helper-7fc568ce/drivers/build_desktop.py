"""Turn one host's extracted P6 numeric archive into a receipt `desktops[]` entry (same shape as
desktop-resource-34dda9fa.json). Reads only retained numeric files; performs no app or desktop work.

  build_desktop.py ROOT HOST FUNCTIONAL_RUN ACTIVE_RUN ENVIRONMENT_JSON PACKAGE_FILE ARCHIVE_RECEIPT
"""
import json, sys
from pathlib import Path

root, host, functional, active = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
environment = json.loads(sys.argv[5]); package_file = sys.argv[6]
archive = json.loads(Path(sys.argv[7]).read_text()) if sys.argv[7] != '-' else None
load = lambda p: json.loads((root / p).read_text())
report, idle = load(f'{functional}/results.json'), load(f'{functional}/new-idle.json')
drivers = root / 'drivers'
check = json.loads((drivers / 'package-check.json').read_text()) if (drivers / 'package-check.json').exists() else None
KEEP = ('name', 'passed', 'state', 'seconds', 'operationId', 'helpersObserved', 'helperGoneAfter')
cases = [{k: c[k] for k in KEEP if k in c and c[k] not in (None, [])} for c in report['results']]
for c in cases:
    if 'helpersObserved' in c:
        c['helpersObserved'] = [{'pid': h['pid'], 'startTicks': str(h['startTicks'])} for h in c['helpersObserved']]
windows = []
for w in idle['windows']:
    rows = load(f"{functional}/new-idle-{w['index']}-samples.json")
    peak = lambda key: max(r['processes'][0]['memory'][key] for r in rows)
    windows.append(dict(index=w['index'], elapsed=w['elapsed'], cpuPercent=w['cpuPercent'], rssPeak=w['rssPeak'],
                        pssPeak=w['pssPeak'], gates=w['gates'],
                        hostLoadMaxima=[max(r['load'][i] for r in rows) for i in range(3)],
                        preflight=load(f"{functional}/quiet-preflight-{w['index']}.json"),
                        privateCleanPeak=peak('Private_Clean'), privateDirtyPeak=peak('Private_Dirty'),
                        swapPeak=peak('Swap')))
family = load(f'{active}/family.json')
keys = ('Rss', 'Pss', 'Private_Clean', 'Private_Dirty', 'Swap')
peaks, peak_loads = {}, {}
for key in keys:
    best = max(family, key=lambda s: sum(p['memory'].get(key, 0) for p in s['processes']))
    peaks[key] = sum(p['memory'].get(key, 0) for p in best['processes'])
    peak_loads[key] = list(best['load'])
resident = {'pid': idle['pid'], 'startTicks': str(idle['startTicks'])}
platforms = {}
for s in load(f'{functional}/family.json'):
    for p in s['processes']:
        platforms.setdefault(p['comm'], set()).update(p['platformLibraries'])
platforms = {comm: sorted(libs) for comm, libs in sorted(platforms.items())}
helper = report['installedHelper'] if check is None else check['helper']
gnome = drivers / 'gnome-active.json'
entry = {
    'host': host, 'desktop': report['desktop'], 'sessionType': report['sessionType'], 'build': report['build'],
    'functionalRun': functional, 'functionalPassed': sum(c['passed'] for c in report['results']),
    'functionalTotal': len(report['results']), 'cases': cases,
    'unknownFindings': load(f'{functional}/unknown-findings.json') if (root / functional / 'unknown-findings.json').exists() else [],
    'uiExit': report['uiClosedBeforeIdle'], 'updateBeforeIdle': report.get('updateBeforeIdle'),
    'settlingSeconds': idle['settlingSecondsAfterUiExit'], 'installedBinaries': idle['binaries'],
    'resident': resident,
    'sameUsedResidentTwoDisjointWindows': len(windows) == 2 and all(all(w['gates'].values()) for w in windows),
    'idleWindows': windows, 'activeRun': active, 'activeFamilyPeakBytes': peaks, 'activePeakHostLoads': peak_loads,
    'activeHostLoadMax': max(s['load'][0] for s in family), 'activeNumbersAreDiagnostic': True,
    'activePassed': all(c['passed'] for c in load(f'{active}/results.json')['results']),
    'residentLibraries': idle['libraries'], 'qtPlatformLibrariesByProcess': platforms,
    'helpersLeft': report['helpersLeft'], 'sampleCadenceSeconds': 0.2,
    'processScope': 'Same-UID putgd-prefixed processes, including CLI and all product helpers; PID/PPID/startTicks/executable, '
                    'RSS/PSS/private memory, CPU ticks, swap and load retained. Finite sampling is not an exhaustive exec trace.',
    'environment': environment,
    'installedPackage': {'file': package_file, 'sha256': check and check['packageSha256'], 'helperSha256': helper['sha256'],
                         'helperPath': helper['path'], 'identity': helper.get('identity'),
                         'sourceCatalogSha256': helper.get('sourceCatalogSha256')},
    'automaticUploadLinkItemsShared': sum(1 for c in report['results'] for i in c.get('items', []) if i.get('link')),
    'extensionActiveForCapture': ('State: ACTIVE' in json.loads(gnome.read_text())['info']) if gnome.exists() else None,
    'regionHelperLifetimes': [c for c in cases if c['name'] in ('region-complete', 'region-cancel')],
    'retainedNumericArchive': archive,
}
entry['status'] = 'passed' if (entry['functionalPassed'] == entry['functionalTotal'] and entry['activePassed'] and idle['passed']
                                and entry['sameUsedResidentTwoDisjointWindows'] and not entry['helpersLeft']
                                and entry['uiExit'].get('code') == 0) else 'failed'
print(json.dumps(entry, indent=2))
