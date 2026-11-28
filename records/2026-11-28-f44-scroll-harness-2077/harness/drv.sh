set -u
cd ~/work/h2077
{
date -u +%T
git clone --filter=blob:none --no-checkout https://github.com/patrick-hudson/put.gd-desktop.git src && cd src && git checkout -q v26.1126.7275-nightly && git status --short | head -3
mkdir -p build && ln -sfn $HOME/work/sdk-1.11.937/build/sdk build/sdk && ln -sfn $HOME/work/sdk-1.11.937/build/dependencies build/dependencies
cmake --preset release -DPUTGD_RELEASE_TAG=v26.1126.7275-nightly && nice cmake --build build/release -j4 --target test_scroll_capture_driver test_scroll_page_fixture
echo "EXIT $?"
date -u +%T
} > ~/work/h2077/build.log 2>&1
echo DONE > ~/work/h2077/build.done
