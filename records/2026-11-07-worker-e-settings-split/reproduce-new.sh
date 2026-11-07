set -eu
cd /home/patrick/work/we1226
export TMPDIR=/tmp/we1226-t XDG_RUNTIME_DIR=/tmp/we1226-r
cmake --preset dev
cmake --build --preset dev --target test_gui_settings_appearance test_gui_settings_general test_gui_settings_capture test_gui_settings_shortcuts test_gui_settings_destinations test_gui_settings_credentials test_gui_settings_updates test_gui_settings_advanced
for area in appearance general capture shortcuts destinations credentials updates advanced; do
 QT_QPA_PLATFORM=offscreen build/dev/test_gui_settings_$area -functions > evidence/$area-functions.txt
 QT_QPA_PLATFORM=offscreen build/dev/test_gui_settings_$area -datatags > evidence/$area-datatags.txt
 sha256sum build/dev/test_gui_settings_$area >> evidence/new-binaries.sha256
done
ctest --preset dev -R '^gui_settings_' --output-junit /home/patrick/work/we1226/evidence/settings.xml > evidence/ctest.log 2>&1
python3 tools/ci/check_test_waits.py > evidence/waits.log
{
 hostname
 uname -a
 qmake6 -query QT_VERSION
 cmake --version
 cat /etc/os-release
} > evidence/host.txt
