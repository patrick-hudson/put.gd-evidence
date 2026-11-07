set -eu
cd /home/patrick/work/we1226
mkdir -m 700 /tmp/we1226-t /tmp/we1226-r
mkdir -p evidence
export TMPDIR=/tmp/we1226-t XDG_RUNTIME_DIR=/tmp/we1226-r QT_QPA_PLATFORM=offscreen
python3 tools/diagnostics/check_socket_paths.py --socket /tmp/we1226-r/putgd/session.sock /tmp/we1226-t/test_gui_settings_destinations-XXXXXX/runtime/putgd/session.sock > evidence/socket-preflight.json
cp build/dev/test_gui_settings evidence/old-binary
sha256sum build/dev/test_gui_settings > evidence/old-binary.sha256
build/dev/test_gui_settings -functions > evidence/old-functions.txt
build/dev/test_gui_settings -datatags > evidence/old-datatags.txt
build/dev/test_gui_settings -maxwarnings 0 -o evidence/old.xml,xml > evidence/old.log 2>&1
