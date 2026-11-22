#!/bin/bash
# Run only under this host's desktop lock.
set -euo pipefail
root=$1
label=$2
step=$3
case "$label" in
    candidate|nightly) ;;
    *) exit 2 ;;
esac
case "$step" in
    plan|apply) ;;
    *) exit 2 ;;
esac
deb="$root/$label.deb"
test "$(dpkg-deb -f "$deb" Package)" = putgd
got=$(dpkg-deb -f "$deb" Version)
args=(install --reinstall --no-install-recommends --allow-downgrades "$deb")
plan="$root/$label.apt.plan"
transaction() {
    awk '/^(Inst|Remv|Conf) / {print}' "$1"
}
check_plan() {
    awk '
      /^Inst / {if ($2 != "putgd") exit 3; installed++}
      /^Conf / {if ($2 != "putgd") exit 3}
      /^Remv / {exit 3}
      END {if (installed!=1) exit 3}
    ' "$1"
}
if [[ "$step" == plan ]]; then
    sudo -n apt-get -s "${args[@]}" > "$plan"
    cat "$plan"
    check_plan "$plan"
else
    check_plan "$plan"
    sudo -n apt-get -s "${args[@]}" > "$plan.recheck"
    cmp <(transaction "$plan") <(transaction "$plan.recheck")
    sudo -n apt-get -o Dpkg::Use-Pty=0 -y "${args[@]}"
    test "$(dpkg-query -W -f='${Version}' putgd)" = "$got"
    putgd --version
fi
