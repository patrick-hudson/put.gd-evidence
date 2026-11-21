"""Hybrid: PP-OCR detector (RapidOCR, ONNX Runtime) for line boxes, then system libtesseract
(C API via ctypes, LSTM, PSM 7) recognizing each line crop on N threads. One JSON line out."""
import ctypes, json, os, sys, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from joiner import join_lines, join_layout, hwm_kib, Sampler
SAMPLER = Sampler()
from concurrent.futures import ThreadPoolExecutor
p = argparse.ArgumentParser()
p.add_argument('image')
p.add_argument('--version', default='PP-OCRv6')
p.add_argument('--det-type', default='tiny')
p.add_argument('--det-lang', default='en')
p.add_argument('--threads', type=int, default=4)
p.add_argument('--tess-threads', type=int, default=4)
p.add_argument('--max-side', type=int, default=4096)
p.add_argument('--det-limit', type=int, default=736)
p.add_argument('--det-limit-type', default='min')
p.add_argument('--pad', type=int, default=4)
p.add_argument('--tessdata', default='/usr/share/tesseract/tessdata')
p.add_argument('--lib', default='libtesseract.so.5')
p.add_argument('--scale-to', type=int, default=0, help='rescale crops so text height is about this many px (0 = off)')
a = p.parse_args()
t0 = time.monotonic()
import numpy as np, cv2
base_py, _ = hwm_kib()
import onnxruntime
from rapidocr import RapidOCR, OCRVersion, ModelType, LangDet
T = ctypes.CDLL(a.lib)
T.TessBaseAPICreate.restype = ctypes.c_void_p
T.TessBaseAPIInit2.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
T.TessBaseAPISetPageSegMode.argtypes = [ctypes.c_void_p, ctypes.c_int]
T.TessBaseAPISetImage.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
T.TessBaseAPISetSourceResolution.argtypes = [ctypes.c_void_p, ctypes.c_int]
T.TessBaseAPIGetUTF8Text.argtypes = [ctypes.c_void_p]
T.TessBaseAPIGetUTF8Text.restype = ctypes.c_void_p
T.TessDeleteText.argtypes = [ctypes.c_void_p]
T.TessBaseAPIEnd.argtypes = [ctypes.c_void_p]
base_all, _ = hwm_kib()
imp_ms = (time.monotonic() - t0) * 1000
t1 = time.monotonic()
eng = RapidOCR(params={
    'Global.use_cls': False, 'Global.use_rec': False, 'Global.log_level': 'error', 'Global.max_side_len': a.max_side,
    'Det.ocr_version': OCRVersion(a.version), 'Det.model_type': ModelType(a.det_type), 'Det.lang_type': LangDet(a.det_lang),
    'Det.limit_side_len': a.det_limit, 'Det.limit_type': a.det_limit_type,
    'EngineConfig.onnxruntime.intra_op_num_threads': a.threads, 'EngineConfig.onnxruntime.inter_op_num_threads': 1,
    'EngineConfig.onnxruntime.enable_cpu_mem_arena': False})
apis = []
for _ in range(a.tess_threads):
    api = T.TessBaseAPICreate()
    # OEM 1 = LSTM only
    if T.TessBaseAPIInit2(api, a.tessdata.encode(), b'eng', 1) != 0:
        raise SystemExit(json.dumps({'error': 'tess init'}))
    T.TessBaseAPISetPageSegMode(api, 7)
    apis.append(api)
load_ms = (time.monotonic() - t1) * 1000
img = cv2.imread(a.image, cv2.IMREAD_COLOR)
grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
H, W = grey.shape
t2 = time.monotonic()
res = eng(img)
det_ms = (time.monotonic() - t2) * 1000
boxes = []
for box in ([] if res.boxes is None else res.boxes):
    xs = [pt[0] for pt in box]; ys = [pt[1] for pt in box]
    boxes.append((max(0, int(min(xs)) - a.pad), max(0, int(min(ys)) - a.pad), min(W, int(max(xs)) + a.pad + 1), min(H, int(max(ys)) + a.pad + 1)))
import queue
pool_q = queue.Queue()
for api in apis:
    pool_q.put(api)

def rec(b):
    x0, y0, x1, y1 = b
    crop = np.ascontiguousarray(grey[y0:y1, x0:x1])
    if a.scale_to and (y1 - y0) > 0:
        f = a.scale_to / max(1, (y1 - y0 - 2 * a.pad))
        if f > 1.05 or f < 0.95:
            crop = np.ascontiguousarray(cv2.resize(crop, None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC if f > 1 else cv2.INTER_AREA))
    api = pool_q.get()
    try:
        T.TessBaseAPISetImage(api, crop.ctypes.data, crop.shape[1], crop.shape[0], 1, crop.strides[0])
        T.TessBaseAPISetSourceResolution(api, 70)
        ptr = T.TessBaseAPIGetUTF8Text(api)
        s = ctypes.string_at(ptr).decode('utf-8', 'replace') if ptr else ''
        if ptr:
            T.TessDeleteText(ptr)
    finally:
        pool_q.put(api)
    return (b[0], b[1], b[2], b[3], ' '.join(s.split()))

t3 = time.monotonic()
with ThreadPoolExecutor(a.tess_threads) as ex:
    items = list(ex.map(rec, boxes))
rec_ms = (time.monotonic() - t3) * 1000
rss, hwm = hwm_kib()
print(json.dumps(dict(above128Ms=SAMPLER.done(), text=join_layout(items, W, H), peakRssKiB=hwm, baseKiB=base_py, baseAllKiB=base_all, engineOnlyKiB=hwm - base_py,
                      loadMs=round(load_ms, 1), engineMs=round(det_ms + rec_ms, 1), detMs=round(det_ms, 1), recMs=round(rec_ms, 1),
                      importMs=round(imp_ms, 1), lines=len(items))))
