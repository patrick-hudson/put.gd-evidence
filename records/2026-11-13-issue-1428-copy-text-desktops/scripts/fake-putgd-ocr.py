#!/usr/bin/python3 -I
# A stand-in for put.gd's putgd-ocr helper, for desktop pipeline checks of
# issue #1428 while the real engine is not in the package under test. It speaks
# the text-job protocol (src/core/TextJobProtocol.h) and recognizes nothing: it
# answers with a fixed line that names the size of the image it was handed, so
# a paste shows that a selected region travelled through the whole pipeline.
# Not a product file. Remove it after the run.
import hashlib, json, os, struct, sys

def frames():
    for line in sys.stdin.buffer:
        yield json.loads(line)

sent = 0
def send(kind, payload):
    global sent
    sent += 1
    sys.stdout.buffer.write(json.dumps({"version": 1, "type": kind, "sequence": str(sent), "payload": payload},
                                       separators=(",", ":")).encode() + b"\n")
    sys.stdout.buffer.flush()

envelope = None
for frame in frames():
    kind, payload = frame["type"], frame["payload"]
    if kind == "bootstrap":
        envelope = {key: payload[key] for key in ("role", "nonce", "generation")}
        send("ready", dict(envelope, build=payload["build"]))
    elif kind == "activate":
        header = os.pread(3, 32, 0)
        magic, version, width, height, stride = struct.unpack("<4sIIII", header[:20])
        assert magic == b"PGTJ" and version == 1
        text = "put.gd fake helper 1428: region %d x %d" % (width, height)
        output = json.dumps({"text": text, "lineTops": [0], "words": [], "candidates": [], "codes": [],
                             "truncated": False, "banded": False, "languagesUsed": ["eng"], "languagesSkipped": [],
                             "timings": {"engineStartMs": 0, "recognizeMs": 0}}, separators=(",", ":")).encode()
        os.pwrite(4, output, 0)
        send("checkpoint", dict(envelope, ok=True, bytes=str(len(output)), sha256=hashlib.sha256(output).hexdigest()))
    elif kind == "checkpointAccepted":
        sys.exit(0)
sys.exit(5)
