cd ~/work/x2064 || exit 1
N=/home/patrick/work/x2064/nightly/src/build/release; C=/home/patrick/work/x2064/cand1/src/build/release; CH=/home/patrick/work/x2064/cand1/pkg/usr/bin/putgd-record
{
python3 x4k.py n-1080 $N/test_scroll_capture_driver /usr/bin/putgd-record $N/test_scroll_page_fixture 1920 1080
python3 x4k.py c-1080 $C/test_scroll_capture_driver $CH $C/test_scroll_page_fixture 1920 1080
python3 x4k.py n-4k $N/test_scroll_capture_driver /usr/bin/putgd-record $N/test_scroll_page_fixture 3840 2160
python3 x4k.py c-4k $C/test_scroll_capture_driver $CH $C/test_scroll_page_fixture 3840 2160
python3 x4k.py c-4k-1cpu $C/test_scroll_capture_driver $CH $C/test_scroll_page_fixture 3840 2160 0
python3 x4k.py n-4k-1cpu $N/test_scroll_capture_driver /usr/bin/putgd-record $N/test_scroll_page_fixture 3840 2160 0
} > x4k.log 2>&1
echo DONE >> x4k.log
