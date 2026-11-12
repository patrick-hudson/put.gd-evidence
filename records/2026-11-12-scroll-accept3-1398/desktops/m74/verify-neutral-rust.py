import liveneutral as l
for d in sorted((l.P/'runs').glob('accept3-ff-rust-*')):
 if (d/'reference-neutral.png').exists():l.verify(d)
