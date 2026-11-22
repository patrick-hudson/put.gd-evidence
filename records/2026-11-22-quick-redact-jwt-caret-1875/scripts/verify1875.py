#!/usr/bin/env python3
"""#1875 pixel check: regions per recognized word, kind from the fixture's rows.

A word is plain ("Card", "id", "=", "add more tests later") and must be unchanged; the
address, card digits and AWS key must be covered by a mark of their kind; every other
word in the crop is part of a JSON web token and must be covered by a key mark."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import verify_core as core

PLAIN = {"Card", "id", "=", "add", "more", "tests", "later"}

def text_of(word):
    return word.get("text") or "".join(word["textPieces"])

def rows(words):
    """Words grouped into rows by their vertical centre."""
    ordered = sorted(range(len(words)), key=lambda i: words[i]["rect"][1] + words[i]["rect"][3] / 2)
    out = []
    for i in ordered:
        x, y, w, h = words[i]["rect"]
        centre = y + h / 2
        if out and abs(out[-1][0] - centre) < h * 0.5:
            out[-1][1].append(i)
        else:
            out.append([centre, [i]])
    return [sorted(r, key=lambda i: words[i]["rect"][0]) for _, r in out]

def kinds(words):
    """Expected kind of each recognized word, from the fixture row it sits on."""
    result = {}
    for row in rows(words):
        texts = [text_of(words[i]) for i in row]
        if any("@" in t for t in texts):
            kind = ["email"] * len(row)
        elif texts[0].lower() == "card":
            kind = ["plain"] + ["card"] * (len(row) - 1)
        elif texts[0].lower() == "id":
            kind = ["plain" if t.lower() in ("id", "=") else "key" for t in texts]
        elif all(t.lower() in {p.lower() for p in PLAIN} for t in texts):
            kind = ["plain"] * len(row)
        else:
            kind = ["key"] * len(row)
        result.update(zip(row, kind))
    return result

def regions(folder):
    doc = json.loads((folder / "inspect-before.json").read_text())["result"]
    words = doc["text"]["words"]
    expected = kinds(words)
    out = []
    for i, word in enumerate(words):
        k = expected[i]
        x, y, w, h = word["rect"]
        pad = 0 if k == "plain" else 2
        out.append([f"{i}:{text_of(word)[:6]}", k, [x - pad, y - pad, x + w + pad, y + h + pad]])
    return out

def main():
    root = Path(sys.argv[1]); expected = json.loads(sys.argv[2])
    ok_all = True
    for folder in sorted(p for p in root.iterdir() if (p / "redacted.png").is_file()):
        case = folder.name.rsplit("-", 1)[0] if folder.name[-1].isdigit() else folder.name
        result = core.analyze(folder, regions(folder))
        counts = {k: v for k, v in result["counts"].items() if v}
        result["expectedNonzeroCounts"] = expected[case]
        result["countsPass"] = counts == expected[case]
        result["pass"] = (result["countsPass"] and result["allSavedMarkPixelsOpaqueBlack"]
                          and not result["changedOutsideMarks"] and all(r["pass"] for r in result["regions"]))
        (folder / "pixels.json").write_text(json.dumps(result, indent=2) + "\n")
        ok_all &= result["pass"]
        bad = [(r["region"], r["expectedKind"], r["kinds"], r["inkPixelsOutsideOpaqueBlackMarks"], r["changedPixels"])
               for r in result["regions"] if not r["pass"]]
        print(folder.name, "PASS" if result["pass"] else "FAIL", counts, bad[:8])
    sys.exit(0 if ok_all else 1)

if __name__ == "__main__":
    main()
