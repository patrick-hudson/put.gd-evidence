#!/bin/bash
# keys.sh RUN: real QEMU keys via QMP, one combo each, check markers after each.
R=$1; G="bash $HOME/work/b1275/g.sh fedora45-budgie ${PORT:-22462}"
k() { python3 ~/work/b1275/hl.py "$R" key "$@"; sleep 0.8; }
snap() { $G 'ls ~/mg/ | grep ^fired- | tr "\n" " "'; echo; }
k a; k ret; sleep 0.5
echo "typed control: $($G 'od -c ~/mg/typed.txt | head -2')"
for combo in "ctrl alt b" "ctrl alt 1" "ctrl shift k" "ctrl shift 1" "ctrl shift f9" "alt f9" "meta_l t" "ctrl alt ret" "print"; do
  before=$($G 'ls ~/mg/ | grep -c ^fired-')
  k $combo; sleep 0.4
  after=$($G 'ls ~/mg/ | grep -c ^fired-')
  echo "combo [$combo] markers $before -> $after : $(snap)"
done
