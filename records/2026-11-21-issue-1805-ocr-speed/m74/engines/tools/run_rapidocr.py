"""One capture through RapidOCR (ONNX Runtime). Prints one JSON line. Run with venv python -I."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argparse
from joiner import join_lines, join_layout, hwm_kib, Sampler
SAMPLER = Sampler()
p = argparse.ArgumentParser()
p.add_argument('image')
p.add_argument('--version', default='PP-OCRv6')
p.add_argument('--det-type', default='small')
p.add_argument('--rec-type', default='small')
p.add_argument('--det-lang', default='en')
p.add_argument('--rec-lang', default='en')
p.add_argument('--det-version')
p.add_argument('--threads', type=int, default=4)
p.add_argument('--max-side', type=int, default=4096)
p.add_argument('--det-limit', type=int, default=736)
p.add_argument('--det-limit-type', default='min')
p.add_argument('--arena', action='store_true')
p.add_argument('--det-only', action='store_true')
p.add_argument('--boxes-out')
p.add_argument('--ep', default='cpu', help='cpu | webgpu | openvino-cpu | openvino-gpu | ncnn-cpu | ncnn-vulkan')
p.add_argument('--ncnn-dir')
p.add_argument('--ncnn-fp32', action='store_true')
p.add_argument('--ep-opt', action='append', default=[])
a = p.parse_args()
t0 = time.monotonic()
import numpy, cv2
base_py, _ = hwm_kib()
import onnxruntime
base_ort, _ = hwm_kib()
from rapidocr import RapidOCR
EP_USED = []
if a.ep.startswith('ncnn'):
    exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ncnn_session.py')).read())
elif a.ep != 'cpu':
    import rapidocr.inference_engine.onnxruntime.main as _m
    _orig = onnxruntime.InferenceSession
    name = {'webgpu': 'WebGpuExecutionProvider', 'openvino-cpu': 'OpenVINOExecutionProvider', 'openvino-gpu': 'OpenVINOExecutionProvider'}[a.ep]
    opts = dict(o.split('=', 1) for o in a.ep_opt)
    if a.ep == 'openvino-cpu': opts.setdefault('device_type', 'CPU')
    if a.ep == 'openvino-gpu': opts.setdefault('device_type', 'GPU')
    def _sess(path, sess_options=None, providers=None):
        s = _orig(path, sess_options=sess_options, providers=[(name, opts), 'CPUExecutionProvider'])
        EP_USED.append(s.get_providers()[0])
        return s
    _m.InferenceSession = _sess
base_all, _ = hwm_kib()
imp_ms = (time.monotonic() - t0) * 1000
dv = a.det_version or a.version
params = {
    'Global.use_cls': False, 'Global.log_level': 'error', 'Global.max_side_len': a.max_side,
    'Global.use_det': True, 'Global.use_rec': not a.det_only,
    'Det.ocr_version': dv, 'Det.model_type': a.det_type, 'Det.lang_type': a.det_lang,
    'Det.limit_side_len': a.det_limit, 'Det.limit_type': a.det_limit_type,
    'Rec.ocr_version': a.version, 'Rec.model_type': a.rec_type, 'Rec.lang_type': a.rec_lang,
    'EngineConfig.onnxruntime.intra_op_num_threads': a.threads,
    'EngineConfig.onnxruntime.inter_op_num_threads': 1,
    'EngineConfig.onnxruntime.enable_cpu_mem_arena': a.arena,
}
from rapidocr import OCRVersion, ModelType, LangDet, LangRec
conv = {'Det.ocr_version': OCRVersion, 'Rec.ocr_version': OCRVersion, 'Det.model_type': ModelType,
        'Rec.model_type': ModelType, 'Det.lang_type': LangDet, 'Rec.lang_type': LangRec}
params = {k: (conv[k](v) if k in conv else v) for k, v in params.items()}
t1 = time.monotonic()
eng = RapidOCR(params=params)
load_ms = (time.monotonic() - t1) * 1000
img = cv2.imread(a.image, cv2.IMREAD_COLOR)
t2 = time.monotonic()
res = eng(img)
eng_ms = (time.monotonic() - t2) * 1000
items = []
boxes = [] if getattr(res, 'boxes', None) is None else res.boxes
txts = getattr(res, 'txts', None) if (getattr(res, 'txts', None) is not None and not a.det_only) else [''] * len(boxes)
for box, t in zip(boxes, txts):
    xs = [pt[0] for pt in box]; ys = [pt[1] for pt in box]
    items.append((float(min(xs)), float(min(ys)), float(max(xs)), float(max(ys)), t))
if a.boxes_out:
    with open(a.boxes_out, 'w') as f:
        json.dump([i[:4] for i in items], f)
text = join_layout(items, img.shape[1], img.shape[0]) if not a.det_only else ''
rss, hwm = hwm_kib()
el = getattr(res, 'elapse_list', None) or getattr(res, 'elapse', None)
first_ms = None
if a.ep != 'cpu' and os.environ.get('BENCH_WARM'):
    t9 = time.monotonic(); res = eng(img); first_ms = eng_ms; eng_ms = (time.monotonic() - t9) * 1000
print(json.dumps(dict(above128Ms=SAMPLER.done(), ep=EP_USED, firstMs=first_ms, text=text, peakRssKiB=hwm, baseKiB=base_py, baseOrtKiB=base_ort, baseAllKiB=base_all,
                      engineOnlyKiB=hwm - base_py, loadMs=round(load_ms, 1), engineMs=round(eng_ms, 1),
                      importMs=round(imp_ms, 1), lines=len(items), elapse=el if isinstance(el, (list, float, int)) else None)))
