# True-end cost of a capture from its helper log: from the last step that
# appended rows to "scroll: ended", and the whole capture's time.
import re, sys
from datetime import datetime
for path in sys.argv[1:]:
    t = lambda line: datetime.strptime(line[:23], '%Y-%m-%dT%H:%M:%S.%f')
    last = end = None; total = ''
    for line in open(path, errors='replace'):
        if 'scroll step: Appended' in line and not re.search(r'appended 0 ', line): last = t(line)
        if 'scroll: ended' in line: end = t(line); total = line[24:].strip()
    print(path.split('/')[-2], 'end cost %.2f s' % (end - last).total_seconds() if last and end else '?', '|', total)
