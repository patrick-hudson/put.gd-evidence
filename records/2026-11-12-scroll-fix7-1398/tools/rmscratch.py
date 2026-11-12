# rmscratch.py DIR MANIFEST : writes the list of every file under DIR to MANIFEST, then deletes exactly those files
# by name and removes the directories that are empty afterwards (never a recursive delete).
import os, sys
root, manifest = os.path.abspath(sys.argv[1]), sys.argv[2]
assert root.startswith(os.path.expanduser('~/work/sf7')), root
files, dirs = [], []
for d, sub, names in os.walk(root, followlinks=False):
    dirs.append(d)
    for n in names:
        files.append(os.path.join(d, n))
    for n in sub:
        if os.path.islink(os.path.join(d, n)):
            files.append(os.path.join(d, n))
with open(manifest, 'w') as f:
    f.write('\n'.join(files) + '\n')
gone = 0
for p in files:
    try:
        os.unlink(p); gone += 1
    except OSError as e:
        print('kept', p, e)
left = 0
for d in sorted(dirs, key=len, reverse=True):
    try:
        os.rmdir(d)
    except OSError:
        left += 1
print('files listed %d, deleted %d, directories not empty %d' % (len(files), gone, left))
