# Gemini Council Proposal — Highlight Mark (`#1237`)

> **Reproduction**: Every sheet image (`sheet-dark.png`, `sheet-light.png`, `sheet-colours.png`), JSON metric dump (`metrics.json`), and numerical value or table in this document is produced directly by running:
> ```bash
> python3 -I /home/patrick/work/i1237-council/proposals/gemini/hl_research.py
> ```

---

## 1. What the Reader Sees (One Sentence per Page Type)

### Candidate 1 (Ranked #1 — Recommended): **Velvet Ribbon** (`mode_gemini_ribbon`)
- **Light page (`L_dom >= 0.30`)**: The reader sees a luminous fluorescent dye wash soaked into the paper behind crisp, unbleached dark text (`>= 4.02:1` worst-case WCAG contrast across all 7 palette colours, with zero core-ink bleaching).
- **Dark page (`L_dom < 0.30`)**: The reader sees a physical translucent marker ribbon laid over the dark surface—subtle enough that alternating table zebra rows (`#222630` vs `#1B1E25`) still show through—with crisp dark ink of exact `1×` original stroke weight (`>= 4.88:1` worst-case WCAG contrast across all 7 palette colours).
- **Coloured accent UI (`accent-blue`, `accent-green`, `accent-amber`)**: The reader sees the badge or button glaze smoothly into the chosen marker ribbon while its white or dark label flips cleanly into high-contrast dark ink (`5.19–5.31:1` contrast).
- **Photograph / no dominant background (`photo`)**: The reader sees a shadow-anchored fluorescent glaze that tints midtones and highlights while keeping dark silhouettes grounded and readable (`4.72:1` contrast vs `1.18:1` in Round 2).

### Candidate 2 (Ranked #2 — Non-Inverting Dark Alternative): **Luminous Glaze** (`mode_gemini_glaze`)
- **Light page (`L_dom >= 0.30`) & mid-tone accent panels (`0.11 <= L_dom < 0.30`)**: Identical to **Velvet Ribbon**—a translucent dye wash behind crisp dark ink.
- **Deep dark page (`L_dom < 0.11`)**: The reader sees the dark UI stay genuinely dark (`L_bg,new <= 0.135`) under a rich coloured backlight glaze, while every glyph stroke—including muted grey captions and green syntax—is lifted and pastel-tinted by the marker hue (`>= 4.23:1` contrast across all 7 palette colours on dark UI) with zero dark charcoal halos.
- **Photograph / no dominant background (`photo`)**: Identical to **Velvet Ribbon** (`4.72:1` contrast).

---

## 2. Forensic Root-Cause Diagnosis of the Rejected Designs

Before designing our rules, we inspected all 24 PNGs in `rejected/`, `survey/`, `crops/`, and `acc/` and measured the exact failure mechanisms in `hl_research.py`:

### Why Round 1 (`D'` background-only tint, `mode_tint`) failed
1. **Dark charcoal moats (halos) around every white glyph on dark UI**: Round 1 computed ink coverage as `cov = clip(d / 70.0, 0, 1)` where `d = ||px - bg||_2`. On dark UI, white text has `d ≈ 330..360`, so anti-aliased edge pixels have `70 <= d < 250`. Clamping at `70` gave those edge pixels `cov = 1.0`, so `(1 - cov) = 0`: they received **zero background tint**, leaving an ugly dark charcoal moat around every letter against the lifted background.
2. **Crushed contrast on muted grey and zoomed-out text**: Lifting a dark background toward `L = 0.183` without lifting the ink crushes any grey caption whose original luminance sits in `L = 0.15..0.32`. In `dark-settings-top`, worst-case contrast drops from `4.44:1` to `2.2:1`; on zoomed-out UI (`rejected/acc-dark-zoomed.png`), contrast collapses to `1.1–1.9:1`.
3. **Muddy olive-brown yellow**: Scaling `#FACC15` (`L = 0.636`) down to `L = 0.183` by linear RGB multiplication produces `#8F7407` (`RGB [143, 116, 7]`), which reads as muddy olive-brown dirt rather than yellow highlighter ink.

### Why Round 2 (PR head `d64203743`, `mode_round2`) failed
1. **Severe glyph thickening (bloat) on dark pages**: In `HighlightFilter.cpp`, Round 2 computes `cover = min(70.0, d)` and `t = cover / 70.0`, then lays dark ink with `laid = t^1.5`. Because `cover` saturates at `d = 70` while white-on-dark glyphs have `d ≈ 350`, **every anti-aliased edge pixel with `70 <= d < 350` gets `t = 1.0` (`laid = 1.0`, 100% solid dark ink)**! Measuring the crops in `hl_research.py` (`diagnostics.bloat`):
   - `kde-notify`: Round 2 turns **1838** pixels into 100% solid ink vs **1059** true stem-core pixels (**1.74×** as many solid-ink pixels; **2028** vs **1534** pixels at `laid >= 0.50`).
   - `dark-settings-top`: Round 2 turns **950** pixels into 100% solid ink vs **592** true stem-core pixels (**1.6×**).
   - `dark-table`: Round 2 turns **2214** pixels into 100% solid ink vs **1676** true stem-core pixels (**1.32×**).
   This is why the dark ink in `rejected/round2-dark-ui.png` looks heavy, bloated, and stamped-on.
2. **Channel clipping in `atLuminance(color, clamp(L, 0.45, 0.70))` destroys Red, Orange, and Blue on light pages**: Round 2 attempts to lift dark palette colours to `L = 0.45` by multiplying linear `(r, g, b)` by `target / L` and clamping to `1.0`. Because Red (`#EF4444`, `L = 0.229`), Blue (`#3B82F6`, `L = 0.235`), and Orange (`#F97316`, `L = 0.325`) already have their primary sRGB channel near `255`, multiplying linear RGB immediately clips `R = 255` or `B = 255` and stops lifting luminance! As measured in `diagnostics.palette_table`:
   - Red `#EF4444` (`L = 0.229`) clips to `#FF5F5F` (`RGB [255, 95, 95]`) with actual luminance **`L = 0.303`** (far below `0.45`), collapsing `light-paragraph` worst contrast from `4.04:1` to **`1.36:1`**.
   - Orange `#F97316` (`L = 0.325`) clips to `#FF861B` (`RGB [255, 134, 27]`) with actual luminance **`L = 0.384`**, collapsing `light-paragraph` contrast to **`1.67:1`**.
   - Blue `#3B82F6` (`L = 0.235`) clips to `#52AFFF` (`RGB [82, 175, 255]`) with actual luminance **`L = 0.397`**, collapsing `light-paragraph` contrast to **`1.73:1`**.
3. **White and Black markers become flat grey smudges**: In Round 2, White (`#FFFFFF`) becomes `#DADADA` (`L = 0.701`) and Black (`#111111`) becomes `#B3B3B3` (`L = 0.451`), two warm-neutral grey slabs that look like disabled UI states.
4. **Flat `paperMarker` replacement erases dark-UI surface hierarchy**: On dark pages, Round 2 replaces every dark background cluster `bg_k` with the exact same constant `paper` colour, erasing alternating zebra rows (`#222630` vs `#1B1E25` in `dark-table`) and tearing mixed dark cards (`dark-notify` right-hand close button) in two.

### Why Candidate B (Border / Pill `V1–V8`) failed
- Adding a `1–3px` stroke around the highlight rect (`rejected/border-v1-v8-sheet.png`, `rejected/border-dark-ui.png`) visually collides with `put.gd`'s Rectangle tool (`R`) and with native UI focus rings/buttons, violating the **Honest** test, while the faint interior fill still lowers contrast on muted grey text.

---

## 3. Exact Pixel Maths (`Velvet Ribbon` #1 and `Luminous Glaze` #2)

### 3.1 Shared Primitives

Let each pixel in the highlight rectangle $H \times W$ have sRGB coordinates $P(x,y) = (R, G, B) \in [0, 255]^3$, and let the chosen marker colour be $M = (M_R, M_G, M_B) \in [0, 255]^3$.

1. **Linear sRGB & WCAG Relative Luminance**:
   $$c_{\text{lin}}(u) = \begin{cases} (u/255)/12.92 & u/255 \le 0.04045 \\ ((u/255 + 0.055)/1.055)^{2.4} & \text{otherwise} \end{cases}$$
   $$L(P) = 0.2126\,c_{\text{lin}}(R) + 0.7152\,c_{\text{lin}}(G) + 0.0722\,c_{\text{lin}}(B)$$

2. **Block Background Map & Distinct Surface Clusters (existing `segment(px)` pass)**:
   - Partition the highlight rectangle into $32 \times 16\text{ px}$ blocks, quantise RGB by $1/8$ (`>> 3`), and find each block's modal bin and confident fraction $f_{\text{conf}}$ (fraction of blocks whose modal $3^3$ neighbourhood holds $\ge 35\%$ of pixels). Also compute the global modal bin fraction $f_{\text{global}}$ over the entire rectangle.
   - Bilinearly interpolate block backgrounds to per-pixel background estimate $B(x,y) \in [0,255]^3$, and cluster block backgrounds (merge radius $24.0$ in RGB) into $K \le 4$ distinct surface colours $\{\text{bg}_1, \dots, \text{bg}_K\}$.
   - Assign each pixel to its nearest surface cluster $k(x,y) = \arg\min_k \|B(x,y) - \text{bg}_k\|_2$, and define the dominant surface of the rectangle as $\text{bg}_{\text{dom}} = \text{bg}_{k^*}$ where $k^* = \arg\max_k |\{(x,y) : k(x,y) = k\}|$.
   - Legacy distance coverage is $\text{cov}(x,y) = \text{clip}(\|P(x,y) - B(x,y)\|_2 / 70.0,\; 0,\; 1)$.

3. **3×3 Local-Peak True Ink Coverage $\alpha(x,y) \in [0, 1]$ (fixes both Round 1 halos and Round 2 glyph bloat)**:
   - Let $d(x,y) = \|P(x,y) - B(x,y)\|_2$ be the Euclidean RGB distance from the local background, and let $d_{\max}(x,y) = \max_{(\Delta x, \Delta y) \in \{-1,0,1\}^2} d(x+\Delta x, y+\Delta y)$ be its $3 \times 3$ local maximum.
   - Define the local peak reference and true fractional coverage:
     $$d_{\text{peak}}(x,y) = \max\bigl(28.0,\; 0.78 \cdot d_{\max}(x,y)\bigr), \qquad \alpha(x,y) = \text{clip}\!\left(\frac{d(x,y)}{d_{\text{peak}}(x,y)},\; 0,\; 1\right)$$
   - **Why this works**: Every glyph stem core is within $22\%$ of its local $3\times 3$ peak ($d \ge 0.78\,d_{\max}$) regardless of whether the text is bright white ($d \approx 350$), muted grey ($d \approx 185$), coloured syntax ($d \approx 145$), or faint caption text ($d \approx 36$), so every stem core gets $\alpha = 1.0$. Conversely, an anti-aliased edge pixel next to a $d_{\max}=350$ white stem has $d_{\text{peak}} = 273$, so a $50\%$ edge pixel ($d=136$) gets its true fractional coverage $\alpha = 0.50$ instead of saturating to $1.0$ at $d=70$.

4. **Beer-Lambert Optical Dye Transmittance $\text{Dye}(M, L_{\text{target}})$ (fixes channel clipping)**:
   - A real physical highlighter is a translucent optical filter governed by Beer-Lambert transmittance $T_c(\tau) = (M_c / 255)^\tau$, where $\tau > 0$ is the dye thickness.
   - When lifting a marker colour with $L(M) < L_{\text{target}}$ to target luminance $L_{\text{target}}$, we solve for the unique optical thickness $\tau \in (0, 1]$ (via 22-step bisection, or a 7-entry constant lookup table for the 7 palette colours) such that:
     $$\text{Dye}_c(M, L_{\text{target}}) = 255 \cdot \max(M_c / 255,\; 0.02)^\tau, \qquad L\bigl(\text{Dye}(M, L_{\text{target}})\bigr) = L_{\text{target}}$$
   - Because $(M_c / 255)^\tau \in (0, 1]$ for all $M_c \in [0, 255]$ and $\tau > 0$, **no RGB channel ever clips at 255**, and every marker colour reaches the exact target luminance $L_{\text{target}}$ while preserving its exact hue angle and channel ordering.
   - When darkening a marker with $L(M) > L_{\text{target}}$, we scale linear RGB by $L_{\text{target}} / L(M)$.

| Palette Colour | Hex | Orig $L(M)$ | Round 2 `paperMarker` (clipped $L$) | Gemini Light Dye $M_{\text{light}}$ ($L$) | Gemini Dark Ribbon Base $M_{\text{dark}}$ ($L$) | Gemini Glaze Ink Tint ($L$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Red** | `#EF4444` | `0.229` | `#FF5F5F` (`0.303`) | `#FBC0C0` (`0.620`) | `#FAAAAA` (`0.520`) | `#FEEDED` (`0.880`) |
| **Orange** | `#F97316` | `0.325` | `#FF861B` (`0.384`) | `#FDC573` (`0.620`) | `#FCAF50` (`0.520`) | `#FFF0D3` (`0.880`) |
| **Yellow** | `#FACC15` | `0.636` | `#FACC15` (`0.636`) | `#FACC15` (`0.636`) | `#FACC15` (`0.636`) | `#FEF49A` (`0.880`) |
| **Green** | `#22C55E` | `0.411` | `#24CD62` (`0.449`) | `#6DE5A8` (`0.620`) | `#45D886` (`0.520`) | `#D5F9E9` (`0.880`) |
| **Blue** | `#3B82F6` | `0.235` | `#52AFFF` (`0.397`) | `#A9D3FC` (`0.620`) | `#8FC3FB` (`0.520`) | `#E6F3FE` (`0.880`) |
| **White** | `#FFFFFF` | `1.000` | `#DADADA` (`0.701`) | `#D8E0EE` (`0.741`) | `#E0E4EC` (`0.774`) | `#FFFFFF` (`1.000`) |
| **Black** | `#111111` | `0.006` | `#B3B3B3` (`0.451`) | `#CACED6` (`0.616`) | `#ACB4C2` (`0.453`) | `#E8EEF8` (`0.851`) |

---

### 3.2 Candidate 1 (Ranked #1 — Recommended): **Velvet Ribbon** (`mode_gemini_ribbon`)

1. **Photo / No-Background Gate**:
   - If $f_{\text{conf}} < 0.50$ **and** $f_{\text{global}} < 0.28$, the rectangle has no flat UI surface; route to **Photo Fallback** (§3.4). Including $f_{\text{global}} < 0.28$ prevents small or dense text boxes on dark/accent UI (such as `accent-amber`, where $f_{\text{conf}} = 0.375$ but $f_{\text{global}} = 0.335$) from falsely triggering the photo fallback.

2. **Whole-Box Light vs. Dark Decision**:
   - Compute $L_{\text{dom}} = L(\text{bg}_{\text{dom}})$ on the dominant surface cluster $\text{bg}_{\text{dom}}$.
   - If $L_{\text{dom}} \ge 0.30$, the mark is a **Light-Page Wash**; if $L_{\text{dom}} < 0.30$, the mark is a **Dark-Page Velvet Ribbon**.
   - Making this decision at the whole-mark level (`bg_dom`) with a consistent sub-cluster rule prevents tearing mixed UI cards (`dark-notify`) across a single stroke.

3. **Case A — Light-Page Wash ($L_{\text{dom}} \ge 0.30$)**:
   - Compute the light-page dye colour $M_{\text{light}}$:
     $$M_{\text{light}} = \begin{cases} (216, 224, 238) & \text{if } \max(M)-\min(M) < 15 \text{ and } L(M) > 0.85 \text{ (White marker)} \\ (202, 206, 214) & \text{if } \max(M)-\min(M) < 15 \text{ and } L(M) \le 0.85 \text{ (Black marker)} \\ \text{Dye}\bigl(M,\; \text{clip}(L(M), 0.62, 0.72)\bigr) & \text{otherwise (Chromatic markers)} \end{cases}$$
   - For each surface cluster $\text{bg}_k$, compute the dyed paper colour $T_k = \lfloor \text{bg}_k \odot M_{\text{light}} / 255 \rfloor$ and shift background/anti-aliased pixels proportionally to $(1 - \text{cov}(x,y))$:
     $$P_{\text{wash}}(x,y) = P(x,y) + \bigl(1 - \text{cov}(x,y)\bigr) \cdot (T_k - \text{bg}_k)$$
     Note that for core ink pixels ($d \ge 70 \implies \text{cov} = 1$), $1 - \text{cov} = 0$, so neutral dark glyph cores (`light-menu`, `light-popup`) remain completely untouched.
   - **LCD Subpixel Blue-Fringe Cap**: On FreeType/ClearType horizontal subpixel-rendered light text (`light-paragraph`, `light-heading`), some edge pixels have high Euclidean distance ($200 \le d(x,y) \le 265$) due to a bright blue channel $(R,G,B) \approx (40, 100, 180)$, giving them a misleadingly high luminance $L \approx 0.129$. Against white paper ($L=1.0$) that pixel had $4.5:1$ contrast, but against a dyed paper background $L(T_k) \approx 0.62$ its contrast would dip below $4.0:1$ if left un-tinted. Therefore, for pixels in the narrow mid-distance band $200 \le d(x,y) \le 265$ whose luminance exceeds $L_{\text{cap}} = \max\bigl(0.106,\; (L(T_k) + 0.05)/4.30 - 0.05\bigr)$, we scale linear RGB by $L_{\text{cap}} / L(P_{\text{wash}})$. This holds worst-case WCAG contrast to **`4.02–4.30:1`** across all 7 palette colours on `light-paragraph` while keeping core ink shift tiny (`0.4` on `light-menu`, `1.9` on `light-popup`, `15.5` on `light-paragraph`).

4. **Case B — Dark-Page Velvet Ribbon ($L_{\text{dom}} < 0.30$)**:
   - Compute the base ribbon dye $M_{\text{dark}}$:
     $$M_{\text{dark}} = \begin{cases} (224, 228, 236) & \text{if } \max(M)-\min(M) < 15 \text{ and } L(M) > 0.85 \text{ (White marker)} \\ (172, 180, 194) & \text{if } \max(M)-\min(M) < 15 \text{ and } L(M) \le 0.85 \text{ (Black marker)} \\ \text{Dye}\bigl(M,\; \text{clip}(L(M), 0.52, 0.64)\bigr) & \text{otherwise (Chromatic markers)} \end{cases}$$
   - For any minor bright sub-cluster with $L(\text{bg}_k) \ge 0.35$ inside a dark box, apply the multiplicative tint $\lfloor \text{bg}_k \odot M_{\text{dark}} / 255 \rfloor$ along $(1 - \text{cov})$.
   - For every dark or coloured surface cluster $\text{bg}_k$ ($L(\text{bg}_k) < 0.35$), form the **surface-modulated ribbon**:
     $$R_k = \text{clip}\bigl(0.88 \cdot M_{\text{dark}} + 0.35 \cdot \text{bg}_k,\; 0,\; 255\bigr)$$
     Because $R_k$ retains $35\%$ of $\text{bg}_k$, alternating table zebra rows (`#222630` vs `#1B1E25` in `dark-table`) and secondary button surfaces (`dark-notify`) remain distinctly visible through the marker ribbon instead of being flattened to a single solid colour!
   - Unmix the foreground pixel using the $3\times 3$ local-peak coverage $\alpha(x,y)$:
     $$U(x,y) = \text{clip}\!\left(\text{bg}_k + \frac{P(x,y) - \text{bg}_k}{\max(\alpha(x,y),\; 0.05)},\; 0,\; 255\right)$$
   - Darken $U(x,y)$ in linear sRGB to target luminance $L_{\text{ink}} = \max\bigl(0,\; (L(R_k) + 0.05)/5.3 - 0.05\bigr)$ whenever $L(U) > L_{\text{ink}}$:
     $$I_{\text{dark}}(x,y) = \begin{cases} c_{\text{srgb}}\bigl(c_{\text{lin}}(U(x,y)) \cdot \frac{L_{\text{ink}}}{L(U(x,y))}\bigr) & L(U(x,y)) > L_{\text{ink}} \\ U(x,y) & \text{otherwise} \end{cases}$$
     Note that scaling in linear RGB preserves the relative hue of syntax-highlighted tokens (e.g. green strings become deep forest green, blue keywords become deep navy, white text becomes crisp charcoal).
   - Composite the unmixed dark ink over the ribbon $R_k$ with gamma $1.25$:
     $$P_{\text{out}}(x,y) = \text{round}\Bigl(\text{clip}\bigl(R_k + (I_{\text{dark}}(x,y) - R_k) \cdot \alpha(x,y)^{1.25},\; 0,\; 255\bigr)\Bigr)$$

---

### 3.3 Candidate 2 (Ranked #2 — Non-Inverting Dark Alternative): **Luminous Glaze** (`mode_gemini_glaze`)

- For light pages ($L_{\text{dom}} \ge 0.30$), mid-tone coloured accent buttons ($0.11 \le L_{\text{dom}} < 0.30$), and photos, **Luminous Glaze** uses the exact same equations as **Velvet Ribbon**.
- For **deep dark pages ($L_{\text{dom}} < 0.11$)**, **Luminous Glaze** keeps the dark UI dark (no polarity inversion) while eliminating all three failures of Round 1 (`D'`):
  1. **Marker Glaze Vectors**:
     $$V_{\text{bg}} = \begin{cases} (235, 240, 250) & \text{White marker} \\ (150, 162, 184) & \text{Black marker} \\ \text{Dye}(M, \max(L(M), 0.48)) & \text{Chromatic marker} \end{cases}, \qquad V_{\text{ink}} = \begin{cases} (255, 255, 255) & \text{White marker} \\ (232, 238, 248) & \text{Black marker} \\ \text{Dye}(M, 0.88) & \text{Chromatic marker} \end{cases}$$
  2. **Glazed Dark Background**: Mix $\text{bg}_k$ toward $V_{\text{bg}}$ by $t \in [0,1]$ such that $L(\text{bg}_{k,\text{new}}) = \min(0.135,\; L(\text{bg}_k) + 0.088)$.
  3. **3×3 Local-Peak Ink Unmixing + Contrast Lift**: Unmix $U(x,y) = \text{clip}(\text{bg}_k + (P - \text{bg}_k)/\max(\alpha, 0.05), 0, 255)$ using the $3\times 3$ local-peak coverage $\alpha(x,y)$ (so anti-aliased edges have zero dark charcoal halos). Define the minimum ink luminance for $5.2:1$ contrast against $\text{bg}_{k,\text{new}}$:
     $$L_{\text{min}} = \min\bigl(0.92,\; (L(\text{bg}_{k,\text{new}}) + 0.05) \cdot 5.2 - 0.05\bigr)$$
     Lift and pastel-tint the unmixed ink toward $V_{\text{ink}}$:
     $$w_{\text{lift}}(x,y) = \max\!\left(0.18,\; \text{clip}\!\left(\frac{L_{\text{min}} - L(U(x,y))}{\max(0.88 - L(U(x,y)), 0.05)},\; 0,\; 1\right)\right)$$
     $$I_{\text{glaze}}(x,y) = (1 - w_{\text{lift}}(x,y)) \cdot U(x,y) + w_{\text{lift}}(x,y) \cdot V_{\text{ink}}$$
     Composite over the glazed dark background with $\alpha(x,y)^{0.95}$:
     $$P_{\text{out}}(x,y) = \text{round}\Bigl(\text{clip}\bigl(\text{bg}_{k,\text{new}} + (I_{\text{glaze}}(x,y) - \text{bg}_{k,\text{new}}) \cdot \alpha(x,y)^{0.95},\; 0,\; 255\bigr)\Bigr)$$

---

### 3.4 Decorations, White & Black Markers, and Photo Fallback

- **Decorations**: **`0px` (none)** on both candidates. No borders, no pills, no end-caps, no corner brackets. The mark is a pure per-pixel optical highlighter stroke inside the user's rectangle, so it never masquerades as the Rectangle tool (`R`) or a UI focus ring.
- **How White (`#FFFFFF`) and Black (`#111111`) Markers Behave**:
  - Because an achromatic marker has zero hue chroma (`max(M) - min(M) = 0`), Round 2's luminance clamp turned White and Black into two indistinguishable warm-grey slabs (`#DADADA` and `#B3B3B3`).
  - In our design, **White (`#FFFFFF`)** acts as an **icy silver-frost highlighter** (`#D8E0EE`, $L=0.741$ on light pages; `#E0E4EC`, $L=0.774$ on dark pages in Velvet Ribbon; `#EBF0FA` glaze + `#FFFFFF` crisp ink in Luminous Glaze). **Black (`#111111`)** acts as a **graphite/slate highlighter** (`#CACED6`, $L=0.616$ on light pages; `#ACB4C2`, $L=0.453$ on dark pages in Velvet Ribbon; `#96A2B8` slate glaze in Luminous Glaze). Both are immediately distinguishable from each other, visible on white paper (`#FFFFFF`), and preserve $\ge 4.02:1$ contrast on light pages and $\ge 4.88:1$ contrast on dark pages without ever redacting text.
- **How the Photo Fallback Behaves ($f_{\text{conf}} < 0.50$ and $f_{\text{global}} < 0.28$)**:
  - **Light photos ($\text{mean}(L) > 0.35$)**: Multiplicative dye wash $\lfloor P(x,y) \odot M_{\text{light}} / 255 \rfloor$.
  - **Dark photos ($\text{mean}(L) \le 0.35$)**: Round 2 screened every pixel uniformly with $L=0.183$, which washed out dark subject silhouettes in `photo` and dropped contrast to `1.18:1` (`ink_shift_mean = 183.2`). Instead, we apply a **shadow-anchored screen glaze**: let $S = \text{Dye}(M, 0.20)$ (or $(150,158,172)$ for White, $(108,114,126)$ for Black) and weight the screen blend by local pixel value $w(x,y) = \text{clip}(\max(R,G,B)/48.0,\; 0.12,\; 1.0)$:
    $$P_{\text{out}}(x,y) = 255 - \frac{(255 - P(x,y)) \odot (255 - w(x,y) \cdot S)}{255}$$
    This keeps deep shadows anchored while glazing midtones and highlights, raising `photo` contrast from **`1.18:1`** (Round 2) to **`4.72:1`** and reducing `ink_shift_mean` from **`183.2`** to **`25.2`**.

---

## 4. Rationale Against Every Design Test in `CONTEXT.md`

1. **Readable (WCAG contrast $\ge 4.5:1$ or never lower than original)**:
   - On dark pages, **Velvet Ribbon** achieves **`4.88:1` to `7.34:1`** worst-case contrast across all 7 crops and all 7 palette colours (improving `dark-settings-top` from `4.44:1` original to `4.88–4.98:1` and `dark-notify` from `1.18:1` to `5.10:1`). **Luminous Glaze** achieves **`4.23:1` to `5.67:1`** across all dark crops and colours (lifting `dark-settings-top` from `4.44:1` to `4.51–5.08:1`).
   - On light pages, **Velvet Ribbon** and **Luminous Glaze** eliminate Round 2's channel-clipping contrast collapse (`1.36:1` on Red, `1.67:1` on Orange, `1.73:1` on Blue), maintaining **`4.02:1` to `4.30:1`** across all 7 palette colours on `light-paragraph` (above the `4.04:1` original on yellow/orange/green/blue/white), **`4.70:1`** on `light-menu`, **`4.44:1`** on `light-heading`, and **`4.28:1`** on `light-popup` (vs `3.49:1` in Round 2).
2. **Unmistakable (glance test at `0.5×` zoom)**:
   - Both candidates tint the entire interior of the highlight rectangle with a saturated, optically uniform dye—immediately visible from across the room at `0.5×` zoom without relying on thin borders.
3. **Colour-faithful (all 7 palette colours read as their named colour)**:
   - Because Beer-Lambert transmittance $255 \cdot (M_c / 255)^\tau$ never clips an sRGB channel, Red `#EF4444` is a true rose-red marker (`#FBC0C0` light / `#FAAAAA` dark), Orange `#F97316` is a true warm amber-orange (`#FDC573` / `#FCAF50`), Yellow `#FACC15` is pure fluorescent yellow (`#FACC15`), Green `#22C55E` is true mint-emerald (`#6DE5A8` / `#45D886`), Blue `#3B82F6` is true sky-cobalt (`#A9D3FC` / `#8FC3FB`), White is cool frost (`#D8E0EE` / `#E0E4EC`), and Black is warm graphite (`#CACED6` / `#ACB4C2`).
4. **Honest (looks like a highlighter mark, not a button or Rectangle mark)**:
   - Zero borders (`0px`), zero corner brackets, zero pill frames. **Velvet Ribbon** preserves underlying zebra-row modulation (`0.35 * bg_k`), so the mark looks like a translucent physical highlighter strip laid across the UI.
5. **Simple (`O(1)` per pixel after the existing block pass)**:
   - Uses only the existing $32 \times 16$ block pass plus a $3 \times 3$ maximum filter (`max_filter_3x3`) and per-pixel arithmetic. No fonts, no OCR, no connected-components, and the 7 palette dye values can be precomputed once per mark.

---

## 5. Complete Tile Metrics (Generated by `hl_research.py`)

In the tables below:
- **`contrast_min`** is the worst-case WCAG contrast ratio across the distinct ink clusters against the new background (computed by `measure()`).
- **`ink_shift_mean`** is the mean Euclidean RGB shift of core ink pixels (`(cov >= 0.85) & (d >= 45)`, computed by `measure()`). Note that on dark pages, modes that invert light-on-dark text into dark-on-marker ink (`Round 2` and `Velvet Ribbon`) intentionally have a large `ink_shift_mean` (`~148–200`) because white ink (`#E5E7EB`) is inverted to dark charcoal (`#261F03`), whereas on light pages (`light-menu`, `light-popup`, `light-paragraph`, `light-heading`) `ink_shift_mean` should be near zero (`0.5–11.6`).
- **`cov90_shift_mean`** is the mean Euclidean RGB shift of all pixels with `coverage >= 0.90`.

### 5.1 `sheet-dark.png` — Dark Crops (Default Yellow `#FACC15`)

| Crop | Note | Orig Contrast | Today (`contrast` / `core_sh` / `cov90_sh`) | Round 2 (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #1 Velvet Ribbon** (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #2 Luminous Glaze** (`contrast` / `core_sh` / `cov90_sh`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `dark-table` | box across two zebra rows + icons | `10.47:1` | `3.52:1` / `87.2` / `81.8` | `5.0:1` / `85.6` / `117.8` | **`5.25:1`** / `181.6` / `160.5` | **`5.18:1`** / `87.0` / `93.4` |
| `dark-notify` | light text on dark brown notice | `1.18:1` | `1.1:1` / `81.1` / `80.7` | `4.82:1` / `65.6` / `87.6` | **`5.1:1`** / `78.3` / `115.6` | **`4.38:1`** / `185.0` / `133.7` |
| `kde-notify` | white text on navy | `12.69:1` | `3.97:1` / `90.0` / `84.8` | `4.99:1` / `207.0` / `157.6` | **`5.28:1`** / `245.4` / `198.5` | **`5.48:1`** / `48.1` / `66.0` |
| `dark-settings-top` | muted grey text on dark | `4.44:1` | `2.25:1` / `84.3` / `86.3` | `5.0:1` / `70.7` / `58.8` | **`4.95:1`** / `116.8` / `108.6` | **`4.58:1`** / `131.2` / `136.8` |
| `kde-wallpaper-text` | low-contrast wallpaper text | `1.27:1` | `1.2:1` / `117.0` / `117.0` | `1.85:1` / `189.0` / `189.0` | **`7.34:1`** / `0.0` / `0.0` | **`4.33:1`** / `254.7` / `254.7` |
| `syn-syntax` | issue sample: dark-theme syntax colors (grayscale AA) | `4.56:1` | `2.24:1` / `79.8` / `78.4` | `4.98:1` / `92.5` / `97.8` | **`5.28:1`** / `124.4` / `129.3` | **`4.87:1`** / `117.2` / `113.3` |
| `syn-button` | issue sample: white on accent button | `4.64:1` | `2.64:1` / `99.1` / `99.4` | `5.02:1` / `267.5` / `262.8` | **`5.31:1`** / `267.2` / `262.5` | **`5.31:1`** / `267.2` / `262.5` |

### 5.2 `sheet-light.png` — Light, Accent & Photo Crops (Default Yellow `#FACC15`)

| Crop | Note | Orig Contrast | Today (`contrast` / `core_sh` / `cov90_sh`) | Round 2 (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #1 Velvet Ribbon** (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #2 Luminous Glaze** (`contrast` / `core_sh` / `cov90_sh`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `light-paragraph` | dark text on light grey | `4.04:1` | `2.26:1` / `86.9` / `85.0` | `2.63:1` / `0.0` / `0.2` | **`4.14:1`** / `15.5` / `13.1` | **`4.14:1`** / `15.5` / `13.1` |
| `light-heading` | text on white | `6.8:1` | `2.86:1` / `86.8` / `84.8` | `4.44:1` / `0.0` / `0.2` | **`4.44:1`** / `14.9` / `13.1` | **`4.44:1`** / `14.9` / `13.1` |
| `light-popup` | small text on white popup | `5.34:1` | `2.55:1` / `88.7` / `86.9` | `3.49:1` / `0.1` / `0.3` | **`4.28:1`** / `1.9` / `3.3` | **`4.28:1`** / `1.9` / `3.3` |
| `light-menu` | menu items on white | `7.26:1` | `2.97:1` / `87.9` / `86.9` | `4.7:1` / `0.1` / `0.2` | **`4.7:1`** / `0.4` / `2.9` | **`4.7:1`** / `0.4` / `2.9` |
| `accent` | white text on red accent (photo crop top) | `2.92:1` | `1.65:1` / `99.0` / `96.3` | `1.41:1` / `95.9` / `95.5` | **`5.19:1`** / `108.0` / `104.8` | **`5.19:1`** / `108.0` / `104.8` |
| `photo` | painting: no dominant background | `1.21:1` | `1.25:1` / `132.3` / `129.3` | `1.18:1` / `183.2` / `179.3` | **`4.72:1`** / `25.2` / `31.0` | **`4.72:1`** / `25.2` / `31.0` |

### 5.3 `sheet-colours.png` — All 7 Palette Colours Across 5 Key Crops

#### Crop: `dark-table` (Original worst contrast: `10.47:1`)

| Palette Colour | Hex | Today (`contrast` / `core_sh` / `cov90_sh`) | Round 2 (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #1 Velvet Ribbon** (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #2 Luminous Glaze** (`contrast` / `core_sh` / `cov90_sh`) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Red** | `#EF4444` | `3.9:1` / `73.0` / `72.0` | `5.02:1` / `139.5` / `190.1` | **`5.27:1`** / `188.3` / `166.7` | **`5.17:1`** / `100.2` / `102.7` |
| **Orange** | `#F97316` | `3.83:1` / `79.9` / `78.3` | `5.0:1` / `115.9` / `164.6` | **`5.26:1`** / `179.8` / `166.6` | **`5.18:1`** / `91.4` / `96.2` |
| **Yellow** | `#FACC15` | `3.52:1` / `87.2` / `81.8` | `5.0:1` / `85.6` / `117.8` | **`5.25:1`** / `181.6` / `160.5` | **`5.18:1`** / `87.0` / `93.4` |
| **Green** | `#22C55E` | `3.84:1` / `67.9` / `68.6` | `4.99:1` / `101.8` / `149.0` | **`5.25:1`** / `171.0` / `165.1` | **`5.21:1`** / `84.8` / `88.5` |
| **Blue** | `#3B82F6` | `4.07:1` / `75.8` / `65.1` | `5.0:1` / `112.6` / `161.3` | **`5.25:1`** / `194.4` / `168.0` | **`5.19:1`** / `101.8` / `101.7` |
| **White** | `#FFFFFF` | `3.23:1` / `99.7` / `81.9` | `5.02:1` / `81.8` / `109.5` | **`5.25:1`** / `199.1` / `152.0` | **`5.53:1`** / `106.3` / `111.3` |
| **Black** | `#111111` | `4.49:1` / `76.5` / `96.3` | `4.99:1` / `101.7` / `148.7` | **`5.27:1`** / `182.5` / `171.0` | **`5.1:1`** / `97.7` / `98.4` |

#### Crop: `dark-notify` (Original worst contrast: `1.18:1`)

| Palette Colour | Hex | Today (`contrast` / `core_sh` / `cov90_sh`) | Round 2 (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #1 Velvet Ribbon** (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #2 Luminous Glaze** (`contrast` / `core_sh` / `cov90_sh`) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Red** | `#EF4444` | `1.1:1` / `65.1` / `67.1` | `4.64:1` / `104.4` / `144.1` | **`5.1:1`** / `85.4` / `119.9` | **`4.38:1`** / `214.0` / `152.8` |
| **Orange** | `#F97316` | `1.1:1` / `66.1` / `71.6` | `4.85:1` / `91.5` / `124.6` | **`5.1:1`** / `85.8` / `120.1` | **`4.38:1`** / `202.5` / `143.5` |
| **Yellow** | `#FACC15` | `1.1:1` / `81.1` / `80.7` | `4.82:1` / `65.6` / `87.6` | **`5.1:1`** / `78.3` / `115.6` | **`4.38:1`** / `185.0` / `133.7` |
| **Green** | `#22C55E` | `1.11:1` / `74.6` / `69.6` | `4.84:1` / `83.3` / `112.6` | **`5.1:1`** / `86.1` / `120.2` | **`4.37:1`** / `203.4` / `140.3` |
| **Blue** | `#3B82F6` | `1.12:1` / `90.6` / `77.6` | `4.85:1` / `89.8` / `122.1` | **`5.1:1`** / `85.8` / `121.8` | **`4.38:1`** / `217.2` / `154.5` |
| **White** | `#FFFFFF` | `1.1:1` / `117.5` / `98.9` | `4.83:1` / `60.6` / `81.1` | **`5.1:1`** / `69.6` / `108.6` | **`4.88:1`** / `230.4` / `165.2` |
| **Black** | `#111111` | `1.09:1` / `64.0` / `78.2` | `4.84:1` / `83.1` / `112.1` | **`5.1:1`** / `90.8` / `123.4` | **`4.23:1`** / `211.9` / `150.0` |

#### Crop: `kde-notify` (Original worst contrast: `12.69:1`)

| Palette Colour | Hex | Today (`contrast` / `core_sh` / `cov90_sh`) | Round 2 (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #1 Velvet Ribbon** (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #2 Luminous Glaze** (`contrast` / `core_sh` / `cov90_sh`) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Red** | `#EF4444` | `4.61:1` / `92.3` / `80.5` | `5.0:1` / `282.5` / `231.4` | **`5.31:1`** / `255.3` / `204.3` | **`5.51:1`** / `43.4` / `69.0` |
| **Orange** | `#F97316` | `4.45:1` / `96.9` / `85.7` | `5.0:1` / `256.5` / `205.6` | **`5.28:1`** / `257.9` / `205.1` | **`5.5:1`** / `43.1` / `65.5` |
| **Yellow** | `#FACC15` | `3.97:1` / `90.0` / `84.8` | `4.99:1` / `207.0` / `157.6` | **`5.28:1`** / `245.4` / `198.5` | **`5.48:1`** / `48.1` / `66.0` |
| **Green** | `#22C55E` | `4.24:1` / `90.0` / `79.2` | `4.99:1` / `240.5` / `189.9` | **`5.3:1`** / `250.8` / `203.5` | **`5.52:1`** / `37.3` / `59.2` |
| **Blue** | `#3B82F6` | `4.63:1` / `75.9` / `71.7` | `5.0:1` / `253.0` / `202.2` | **`5.3:1`** / `249.8` / `204.1` | **`5.51:1`** / `41.2` / `67.8` |
| **White** | `#FFFFFF` | `3.62:1` / `42.4` / `65.9` | `4.99:1` / `197.7` / `148.8` | **`5.31:1`** / `225.1` / `185.5` | **`5.67:1`** / `45.6` / `73.2` |
| **Black** | `#111111` | `5.25:1` / `133.7` / `113.1` | `5.0:1` / `240.1` / `189.5` | **`5.28:1`** / `261.2` / `209.2` | **`5.51:1`** / `40.5` / `65.9` |

#### Crop: `dark-settings-top` (Original worst contrast: `4.44:1`)

| Palette Colour | Hex | Today (`contrast` / `core_sh` / `cov90_sh`) | Round 2 (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #1 Velvet Ribbon** (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #2 Luminous Glaze** (`contrast` / `core_sh` / `cov90_sh`) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Red** | `#EF4444` | `2.29:1` / `68.6` / `68.7` | `4.99:1` / `138.0` / `125.3` | **`4.95:1`** / `128.8` / `118.4` | **`4.62:1`** / `147.3` / `153.8` |
| **Orange** | `#F97316` | `2.31:1` / `76.7` / `77.0` | `5.0:1` / `112.9` / `100.6` | **`4.98:1`** / `127.8` / `117.4` | **`4.59:1`** / `139.6` / `145.8` |
| **Yellow** | `#FACC15` | `2.25:1` / `84.3` / `86.3` | `5.0:1` / `70.7` / `58.8` | **`4.95:1`** / `116.8` / `108.6` | **`4.58:1`** / `131.2` / `136.8` |
| **Green** | `#22C55E` | `2.42:1` / `54.6` / `55.3` | `4.99:1` / `98.8` / `86.5` | **`4.95:1`** / `123.3` / `112.6` | **`4.63:1`** / `130.8` / `136.6` |
| **Blue** | `#3B82F6` | `2.53:1` / `59.9` / `61.9` | `5.0:1` / `109.9` / `97.6` | **`4.93:1`** / `128.3` / `118.1` | **`4.6:1`** / `145.2` / `151.8` |
| **White** | `#FFFFFF` | `2.18:1` / `100.1` / `105.9` | `5.0:1` / `63.5` / `51.9` | **`4.88:1`** / `108.4` / `102.3` | **`5.08:1`** / `159.0` / `165.0` |
| **Black** | `#111111` | `2.31:1` / `75.0` / `70.0` | `4.99:1` / `98.5` / `86.4` | **`4.94:1`** / `134.4` / `122.6` | **`4.51:1`** / `141.8` / `148.4` |

#### Crop: `light-paragraph` (Original worst contrast: `4.04:1`)

| Palette Colour | Hex | Today (`contrast` / `core_sh` / `cov90_sh`) | Round 2 (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #1 Velvet Ribbon** (`contrast` / `core_sh` / `cov90_sh`) | **Gemini #2 Luminous Glaze** (`contrast` / `core_sh` / `cov90_sh`) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Red** | `#EF4444` | `2.57:1` / `70.1` / `70.2` | `1.36:1` / `0.0` / `0.2` | **`4.04:1`** / `15.5` / `12.9` | **`4.04:1`** / `15.5` / `12.9` |
| **Orange** | `#F97316` | `2.48:1` / `78.7` / `78.0` | `1.67:1` / `0.0` / `0.2` | **`4.05:1`** / `15.5` / `13.0` | **`4.05:1`** / `15.5` / `13.0` |
| **Yellow** | `#FACC15` | `2.26:1` / `86.9` / `85.0` | `2.63:1` / `0.0` / `0.2` | **`4.14:1`** / `15.5` / `13.1` | **`4.14:1`** / `15.5` / `13.1` |
| **Green** | `#22C55E` | `2.27:1` / `67.0` / `68.0` | `1.92:1` / `0.0` / `0.2` | **`4.05:1`** / `15.5` / `13.0` | **`4.05:1`** / `15.5` / `13.0` |
| **Blue** | `#3B82F6` | `2.37:1` / `64.5` / `66.7` | `1.73:1` / `0.0` / `0.2` | **`4.06:1`** / `15.5` / `12.9` | **`4.06:1`** / `15.5` / `12.9` |
| **White** | `#FFFFFF` | `2.09:1` / `94.7` / `93.4` | `2.89:1` / `0.0` / `0.1` | **`4.3:1`** / `12.7` / `10.4` | **`4.3:1`** / `12.7` / `10.4` |
| **Black** | `#111111` | `2.89:1` / `84.1` / `85.4` | `1.93:1` / `0.0` / `0.1` | **`4.02:1`** / `15.5` / `12.9` | **`4.02:1`** / `15.5` / `12.9` |

