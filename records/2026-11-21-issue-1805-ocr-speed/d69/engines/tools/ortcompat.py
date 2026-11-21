import sys, numpy as np, onnxruntime as ort
print("ort", ort.__version__)
for f, shp in ((sys.argv[1], (1, 3, 736, 1280)), (sys.argv[2], (2, 3, 48, 320))):
    s = ort.InferenceSession(f, providers=["CPUExecutionProvider"])
    x = np.random.default_rng(0).standard_normal(shp).astype(np.float32)
    y = s.run(None, {s.get_inputs()[0].name: x})[0]
    print(f.rsplit("/", 1)[-1], "ok", y.shape, float(y.sum()))
