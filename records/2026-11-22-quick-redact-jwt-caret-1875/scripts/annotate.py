import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
R = Path(sys.argv[1])
RED = (215, 38, 61)
def font(size):
    for f in ("/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf", "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf"):
        try: return ImageFont.truetype(f, size)
        except OSError: pass
    return ImageFont.load_default()
def crop_of(folder):
    return json.loads((folder / "inspect-after.json").read_text())["result"]["crop"]
def panel(folder, title, box, note, good):
    img = Image.open(folder / "redacted.png").convert("RGB")
    cx, cy, _, _ = crop_of(folder)
    head = 44
    out = Image.new("RGB", (img.width + 8, img.height + head + 8), "white")
    out.paste(img, (4, head + 4))
    d = ImageDraw.Draw(out)
    d.text((6, 8), title, fill=(30, 30, 30), font=font(22))
    if box:
        x, y, w, h = box
        x, y = x - cx + 4, y - cy + head + 4
        color = (20, 140, 60) if good else RED
        d.rectangle((x - 6, y - 6, x + w + 6, y + h + 6), outline=color, width=4)
        tw = d.textlength(note, font=font(20))
        ty = y + h + 10 if y + h + 40 < out.height else y - 34
        d.rectangle((x - 6, ty - 2, x - 6 + tw + 12, ty + 26), fill=color)
        d.text((x, ty), note, fill="white", font=font(20))
    return out
def pair(left, right, name):
    w = left.width + right.width + 16
    out = Image.new("RGB", (w, max(left.height, right.height)), (200, 200, 200))
    out.paste(left, (0, 0)); out.paste(right, (left.width + 16, 0))
    out.save(R / "pictures" / name)
# Firefox text field (m74): JWT behind the caret, read kyJ…
b, a = R / "m74/before/browser-1", R / "m74/final/browser-1"
row = [67, 343, 837, 29]
pair(panel(b, "Before (26.1122.6373 aa202c7a, m74)", row, "JWT behind the caret left readable", False),
     panel(a, "After (26.1122.6447 be4949472, m74)", row, "covered", True), "m74-firefox-field-before-after.png")
b, a = R / "k72/before/browser-1", R / "k72/final/browser-1"
pair(panel(b, "Before (26.1122.6374 ffeead0f, k72)", row, "JWT behind the caret left readable", False),
     panel(a, "After (26.1122.6447 be4949472, k72)", row, "covered", True), "k72-firefox-field-before-after.png")
# Kate (k72): caret read with the e as byJ
b, a = R / "k72/before/editor-2", R / "k72/final/editor-2"
row = [210, 304, 811, 29]
pair(panel(b, "Before (26.1122.6374 ffeead0f, k72 Kate)", row, "first row of the JWT left readable", False),
     panel(a, "After (26.1122.6447 be4949472, k72 Kate)", row, "covered", True), "k72-kate-before-after.png")
# m74 xed and terminal after, with the other kinds
for host, case, label in (("m74", "editor-1", "xed"), ("m74", "terminal-1", "xterm"), ("k72", "terminal-1", "xterm")):
    f = R / host / "final" / case
    panel(f, f"After (26.1122.6447 be4949472, {host} {label}): JWT, address, card, AWS key", None, "", True).save(R / "pictures" / f"{host}-{label}-after.png")
