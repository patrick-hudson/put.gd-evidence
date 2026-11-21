# exec'd by run_rapidocr.py: replaces ORT sessions inside RapidOCR with ncnn nets (CPU or Vulkan).
import ncnn, numpy as _np
from pathlib import Path as _P
import rapidocr.inference_engine.onnxruntime.main as _m
_orig = onnxruntime.InferenceSession
_gpu = a.ep == 'ncnn-vulkan'
NCNN_T = {}
class _NcnnSession:
    def __init__(self, path, sess_options=None, providers=None):
        meta = _orig(str(path), providers=['CPUExecutionProvider'])
        self._i, self._o, self._meta = meta.get_inputs(), meta.get_outputs(), meta.get_modelmeta()
        del meta
        stem = _P(path).stem.replace('-', '_')
        t = time.monotonic()
        self.net = ncnn.Net()
        self.net.opt.use_vulkan_compute = _gpu
        self.net.opt.num_threads = a.threads
        if a.ncnn_fp32:
            self.net.opt.use_fp16_packed = self.net.opt.use_fp16_storage = self.net.opt.use_fp16_arithmetic = False
        d = _P(a.ncnn_dir)
        self.net.load_param(str(d / (stem + '.ncnn.param')))
        self.net.load_model(str(d / (stem + '.ncnn.bin')))
        NCNN_T[stem] = round((time.monotonic() - t) * 1000, 1)
        EP_USED.append('ncnn-vulkan' if _gpu else 'ncnn-cpu')
    def get_inputs(self): return self._i
    def get_outputs(self): return self._o
    def get_modelmeta(self): return self._meta
    def get_providers(self): return ['CPUExecutionProvider']
    def run(self, names, feed):
        x = next(iter(feed.values()))
        outs = []
        for n in range(x.shape[0]):
            ex = self.net.create_extractor()
            ex.input('in0', ncnn.Mat(_np.ascontiguousarray(x[n], dtype=_np.float32)))
            _, o = ex.extract('out0')
            outs.append(_np.array(o))
        return [_np.stack(outs)]
EP_USED = []
_m.InferenceSession = _NcnnSession
