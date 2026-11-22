#!/usr/bin/env python3
"""Split synthetic OCR strings in evidence and index words intersecting each mark."""
from pathlib import Path
import json
import sys

def read(path):
    return json.loads(path.read_text())

def write(path, doc):
    path.write_text(json.dumps(doc, indent=2) + "\n")

def overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    width = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    height = max(0, min(ay + ah, by + bh) - max(ay, by))
    return width * height

def split_words(document):
    words = document["result"].get("text", {}).get("words", [])
    for word in words:
        if "text" in word:
            word_text = word.pop("text")
            word["textPieces"] = [word_text[i:i + 8] for i in range(0, len(word_text), 8)]
    return words

def main(root):
    for pre in root.glob("*/*/*/inspect-before.json"):
        post = pre.with_name("inspect-after.json")
        a, b = read(pre), read(post)
        words = split_words(a)
        split_words(b)
        by_mark = [{
            "id": mark["id"], "suggested": mark["suggested"], "rect": mark["rect"],
            "wordIndices": [i for i, word in enumerate(words)
                            if 2 * overlap(word["rect"], mark["rect"]) >= word["rect"][2] * word["rect"][3]],
        } for mark in b["result"]["shapes"]]
        write(pre, a)
        write(post, b)
        write(pre.with_name("mark-ocr.json"), {"marks": by_mark})

if __name__ == "__main__":
    main(Path(sys.argv[1]))
