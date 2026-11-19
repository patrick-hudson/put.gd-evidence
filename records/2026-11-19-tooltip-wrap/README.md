# Long tooltips wrap to a reading width

What was tested: hovering over controls with long tooltips in the real put.gd Settings window, before and after the change.

- Host: m74, Linux Mint 22.3 Cinnamon on X11, 1920x1080, physical desktop, private put.gd profile.
- Before: nightly 26.1118.5367 AppImage (`putgd-26.1118.5367-nightly-x86_64.AppImage`).
- After: branch `fix/tooltip-wrap` at commit 43236dd14, built on m74 with the dev preset (`putgd`, `putgd-ui`, `putgd-cli`).
- The pointer was moved with xdotool onto each control and the full screen was captured with `import -window root` after 2.5 s. The red boxes mark the tooltip.

Result: the long "Unlock saved credentials" tip was one line across the screen, pushed to the left edge. It is now five lines that start at the pointer. The action bar's Upload clipboard tip wraps and stays 8 px inside the right screen edge. Short tips stay on one line.

The before and after frames use different color schemes (light for the AppImage, dark for the build tree). The color scheme is not part of this change.
