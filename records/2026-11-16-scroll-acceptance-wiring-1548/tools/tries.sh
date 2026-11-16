#!/bin/bash
# tries.sh ROOT LABEL N START JITTER : N tries of ptrial.py against lres.py's resident in ROOT,
# Wikipedia "Linux" opened in a fresh Firefox (own profile) before each, closed by its exact PID after.
# Env: FF (firefox binary), MOUSE (umouse command), RECT (default 240,200,1440,820), URL.
here=$(cd "$(dirname "$0")" && pwd)
root=$1; label=$2; n=$3; start=$4; jitter=$5
rect=${RECT:-240,200,1440,820}
url=${URL:-https://en.wikipedia.org/wiki/Linux}
eval "$(python3 -c 'import json,sys,shlex; e=json.load(open(sys.argv[1])); print("\n".join("export %s=%s" % (k, shlex.quote(v)) for k, v in e.items()))' "$root/env.json")"
cli=$(python3 -c 'import json,sys,shlex; print(shlex.join(json.load(open(sys.argv[1]))))' "$root/cli.json")
out=$root/$label.jsonl
i=1
while [ "$i" -le "$n" ]; do
    mkdir -p "$root/ff-profile-$label-$i"
    printf 'user_pref("browser.shell.checkDefaultBrowser", false);\nuser_pref("browser.aboutwelcome.enabled", false);\nuser_pref("browser.sessionstore.resume_from_crash", false);\nuser_pref("datareporting.policy.dataSubmissionEnabled", false);\nuser_pref("browser.startup.homepage_override.mstone", "ignore");\n' > "$root/ff-profile-$label-$i/user.js"
    MOZ_DBUS_REMOTE=0 "${FF:-firefox}" --new-instance --no-remote --profile "$root/ff-profile-$label-$i" "$url" > "$root/firefox.log" 2>&1 &
    ff=$!
    sleep "${LOAD:-9}"
    python3 "$here/ptrial.py" --cli "$cli" --rect "$rect" --log "$root/helper.log" --label "$label-$i" --start "$start" --jitter "$jitter" --mouse "${MOUSE:-sudo -n python3 $here/umouse.py}" >> "$out" 2>> "$root/$label.err"
    kill "$ff" 2>/dev/null; wait "$ff" 2>/dev/null
    sleep 2
    i=$((i + 1))
done
echo done > "$root/$label.done"
