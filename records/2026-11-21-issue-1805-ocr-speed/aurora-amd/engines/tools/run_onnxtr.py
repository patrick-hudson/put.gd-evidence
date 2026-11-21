"""One capture through OnnxTR (docTR models on ONNX Runtime). Prints one JSON line."""
import json, os, sys, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from joiner import join_lines, join_layout, hwm_kib, Sampler
SAMPLER = Sampler()
p = argparse.ArgumentParser()
p.add_argument('image')
p.add_argument('--det', default='fast_base')
p.add_argument('--reco', default='crnn_mobilenet_v3_small')
p.add_argument('--threads', type=int, default=4)
a = p.parse_args()
t0 = time.monotonic()
import numpy, cv2
base_py, _ = hwm_kib()
import onnxruntime as ort
base_ort, _ = hwm_kib()
from onnxtr.models import ocr_predictor, EngineConfig
base_all, _ = hwm_kib()
imp_ms = (time.monotonic() - t0) * 1000
so = ort.SessionOptions()
so.intra_op_num_threads = a.threads
so.inter_op_num_threads = 1
so.enable_cpu_mem_arena = False
cfg = EngineConfig(providers=[('CPUExecutionProvider', {'arena_extend_strategy': 'kSameAsRequested'})], session_options=so)
t1 = time.monotonic()
pred = ocr_predictor(det_arch=a.det, reco_arch=a.reco, assume_straight_pages=True, straighten_pages=False,
                     detect_orientation=False, detect_language=False, disable_crop_orientation=True,
                     disable_page_orientation=True, det_engine_cfg=cfg, reco_engine_cfg=cfg, clf_engine_cfg=cfg)
load_ms = (time.monotonic() - t1) * 1000
img = cv2.cvtColor(cv2.imread(a.image, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
h, w = img.shape[:2]
t2 = time.monotonic()
doc = pred([img])
eng_ms = (time.monotonic() - t2) * 1000
items = []
for block in doc.pages[0].blocks:
    for line in block.lines:
        (x0, y0), (x1, y1) = line.geometry
        items.append((x0 * w, y0 * h, x1 * w, y1 * h, ' '.join(wd.value for wd in line.words)))
rss, hwm = hwm_kib()
print(json.dumps(dict(above128Ms=SAMPLER.done(), text=join_layout(items, w, h), peakRssKiB=hwm, baseKiB=base_py, baseOrtKiB=base_ort, baseAllKiB=base_all,
                      engineOnlyKiB=hwm - base_py, loadMs=round(load_ms, 1), engineMs=round(eng_ms, 1),
                      importMs=round(imp_ms, 1), lines=len(items))))
