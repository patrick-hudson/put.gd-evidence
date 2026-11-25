# drv.sh DIR REF [RELEASE_TAG]: blobless clone at REF, build the lab driver against the m74 SDK.
set -u
D=$1; REF=$2; TAG=${3:-}
cd $D/src || exit 1
{
mkdir -p build && ln -sfn /home/patrick/work/sdk-1.11.937/build/sdk build/sdk && ln -sfn /home/patrick/work/sdk-1.11.937/build/dependencies build/dependencies
cmake --preset release ${TAG:+-DPUTGD_RELEASE_TAG=$TAG} && nice cmake --build build/release -j4 --target test_scroll_capture_driver test_scroll_page_fixture
echo "EXIT $?"
} > $D/build.log 2>&1
echo DONE > $D/build.done
