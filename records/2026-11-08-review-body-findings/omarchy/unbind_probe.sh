set +e
n(){ hyprctl -j binds | python3 -c "import json,sys;d=json.load(sys.stdin);print(len(d),\"binds\", [ (b.get(\"description\"),b.get(\"modmask\"),b.get(\"key\"),b.get(\"submap\")) for b in d if b.get(\"description\",\"\").startswith(\"t:\")])"; }
pid(){ pgrep -x Hyprland || pgrep -x hyprland; }
echo PID $(pid); hyprctl version | head -2; n
echo "--- bind test chords"
hyprctl eval "hl.bind(\"CTRL + SHIFT + F9\", hl.dsp.exec_cmd(\"true\"), { description = \"t:ctrl-shift\" })"
hyprctl eval "hl.bind(\"CTRL + F9\", hl.dsp.exec_cmd(\"true\"), { description = \"t:ctrl\" })"
hyprctl eval "hl.bind(\"SHIFT + F9\", hl.dsp.exec_cmd(\"true\"), { description = \"t:shift\" })"
hyprctl eval "hl.bind(\"F9\", hl.dsp.exec_cmd(\"true\"), { description = \"t:plain\" })"
hyprctl eval "hl.bind(\"CTRL + SHIFT + F8\", hl.dsp.global(\"putgd:probe\"), { description = \"t:global\" })"
hyprctl eval "hl.bind(\"CTRL + SHIFT + F7\", hl.dsp.exec_cmd(\"true\"), { description = \"t:other-runtime\" })"
n
echo "--- unbind exact chord CTRL+SHIFT+F9"
hyprctl eval "hl.unbind(\"CTRL + SHIFT + F9\")"; n; echo PID $(pid)
echo "--- unbind global-dispatch bind"
hyprctl eval "hl.unbind(\"CTRL + SHIFT + F8\")"; n; echo PID $(pid)
echo "--- unbind a chord nothing has"
hyprctl eval "hl.unbind(\"CTRL + SHIFT + F6\")"; n; echo PID $(pid)
echo "--- two binds same chord"
hyprctl eval "hl.bind(\"CTRL + ALT + F9\", hl.dsp.exec_cmd(\"true\"), { description = \"t:dup1\" })"
hyprctl eval "hl.bind(\"CTRL + ALT + F9\", hl.dsp.exec_cmd(\"true\"), { description = \"t:dup2\" })"
n
hyprctl eval "hl.unbind(\"CTRL + ALT + F9\")"; n; echo PID $(pid)
echo "--- submap"
hyprctl eval "hl.define_submap(\"tprobe\", function() hl.bind(\"CTRL + ALT + F10\", hl.dsp.exec_cmd(\"true\"), { description = \"t:submap\" }) end)"
hyprctl eval "hl.bind(\"CTRL + ALT + F10\", hl.dsp.exec_cmd(\"true\"), { description = \"t:global-map\" })"
n
hyprctl eval "hl.unbind(\"CTRL + ALT + F10\")"; n; echo PID $(pid)
echo "--- code: same physical key"
hyprctl eval "hl.bind(\"CTRL + ALT + code:10\", hl.dsp.exec_cmd(\"true\"), { description = \"t:code10\" })"
hyprctl eval "hl.bind(\"CTRL + ALT + 1\", hl.dsp.exec_cmd(\"true\"), { description = \"t:sym1\" })"
n
hyprctl binds | grep -B1 -A12 "t:code10" | head -30
hyprctl eval "hl.unbind(\"CTRL + ALT + 1\")"; n; echo PID $(pid)
echo "--- reload drops other runtime bind?"
hyprctl reload; sleep 2; n; echo PID $(pid)
