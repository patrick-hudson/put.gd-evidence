#!/usr/bin/env python3
"""Check opacity, changed pixels and coverage against visually registered fixture regions."""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

def rectangle(rect):
    x, y, w, h = rect
    return (x, y, x + w, y + h)

def intersects(a, b):
    return (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))

def read(path):
    return json.loads(path.read_text())

def analyze(folder, regions):
    before = Image.open(folder / "capture.png").convert("RGBA")
    after = Image.open(folder / "redacted.png").convert("RGBA")
    assert before.size == after.size
    inspection = read(folder / "inspect-after.json")["result"]
    crop_x, crop_y, width, height = inspection["crop"]
    assert before.size == (width, height)
    bounds = (0, 0, width, height)
    to_local = lambda box: tuple(value - (crop_x, crop_y)[i % 2] for i, value in enumerate(box))
    union = Image.new("L", before.size)
    shapes = []
    for shape in inspection["shapes"]:
        x0, y0, x1, y1 = intersects(to_local(rectangle(shape["rect"])), bounds)
        assert x0 < x1 and y0 < y1
        pixels = after.crop((x0, y0, x1, y1)).getdata()
        black = sum(px == (0, 0, 0, 255) for px in pixels)
        ImageDraw.Draw(union).rectangle((x0, y0, x1 - 1, y1 - 1), fill=255)
        shapes.append(dict(shape, savedIntersection=[x0, y0, x1, y1], opaqueBlackPixels=black,
                           intersectionPixels=(x1 - x0) * (y1 - y0)))
    difference = ImageChops.difference(before, after)
    changed_outside = sum(any(px) and not marked for px, marked in
                          zip(difference.getdata(), union.getdata()))
    output = []
    for name, kind, box in regions:
        x0, y0, x1, y1 = intersects(to_local(box), bounds)
        assert x0 < x1 and y0 < y1
        ink = 0
        uncovered = 0
        touched = 0
        right_kind = 0
        ink_changed = 0
        hits = {}
        for y in range(y0, y1):
            for x in range(x0, x1):
                pixel = before.getpixel((x, y))
                if max(pixel[:3]) >= 208:
                    continue
                ink += 1
                if pixel != after.getpixel((x, y)):
                    ink_changed += 1
                mark_ids = []
                for shape in shapes:
                    sx, sy, ex, ey = shape["savedIntersection"]
                    if sx <= x < ex and sy <= y < ey:
                        mark_ids.append(shape["id"])
                        hits[shape["id"]] = hits.get(shape["id"], 0) + 1
                if mark_ids:
                    touched += 1
                if any(s["id"] in mark_ids and s["suggested"] == kind for s in shapes):
                    right_kind += 1
                if not mark_ids or after.getpixel((x,y)) != (0, 0, 0, 255):
                    uncovered += 1
        kinds = sorted({s["suggested"] for s in shapes if s["id"] in hits})
        inside_change = sum(any(px) for px in difference.crop((x0, y0, x1, y1)).getdata())
        ok = ink > 0 and (not inside_change if kind == "plain" else not uncovered and right_kind == ink)
        output.append({"region": name, "expectedKind": kind, "rectDesktopEdges": box,
                       "inkPixels": ink, "changedPixels": inside_change, "changedInkPixels": ink_changed,
                       "inkPixelsInsideAnyMark": touched, "inkPixelsInsideExpectedKind": right_kind, "inkPixelsOutsideOpaqueBlackMarks": uncovered,
                       "inkPixelsByMark": hits, "kinds": kinds, "pass": ok})
    counts = read(folder / "apply.json")["result"]["counts"]
    expected = {
        "1": {"key": 2, "card": 2}, "2": {"key": 1, "email": 1}, "3": {"key": 2},
        "4": {"key": 1}, "6": {"key": 1, "card": 2},
    }.get(folder.name, {"key": 1})
    count_pass = {k: v for k, v in counts.items() if v} == expected
    marks_pass = all(s["opaqueBlackPixels"] == s["intersectionPixels"] for s in shapes)
    return {"counts": counts, "expectedNonzeroCounts": expected, "countsPass": count_pass,
            "allSavedMarkPixelsOpaqueBlack": marks_pass, "changedOutsideMarks": changed_outside,
            "marks": shapes, "regions": output,
            "pass": count_pass and marks_pass and not changed_outside and all(r["pass"] for r in output)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("regions", type=Path)
    args = parser.parse_args()
    regions = read(args.regions)
    for folder in sorted(args.folder.iterdir()):
        if folder.name not in regions or not (folder / "redacted.png").is_file():
            continue
        result = analyze(folder, regions[folder.name])
        (folder / "pixels.json").write_text(json.dumps(result, indent=2) + "\n")
        print(folder.name, result["pass"], result["counts"],
              [(r["region"], r["kinds"], r["inkPixelsOutsideOpaqueBlackMarks"])
               for r in result["regions"]])

if __name__ == "__main__":
    main()
