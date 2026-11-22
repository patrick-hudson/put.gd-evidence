"""Recreate the unsuccessful first control and the subsequent contrast sweep."""
from pathlib import Path
import sys
from fixtures import generate, whole_screen

root = Path(sys.argv[1])
rows = generate(root, int(sys.argv[2]))
for i, (size, color) in enumerate(
        [(21, '#46505b'), (21, '#424854'), (24, '#424953'),
         (24, '#454b57'), (24, '#484e5b'), (26, '#444a55'), (26, '#5c6370')], 1):
    whole_screen(root, rows[9][1], name=f'-v{i}', font_px=size, ink=color, equal_background=True)

for i, (ink, bright) in enumerate([('#454b57', '#5a626d'), ('#454b57', '#646b77'),
                                    ('#454b57', '#515964'), ('#474c59', '#555c68')], 8):
    whole_screen(root, rows[9][1], name=f'-v{i}', font_px=26, ink=ink,
                 equal_background=True, bright=bright)
