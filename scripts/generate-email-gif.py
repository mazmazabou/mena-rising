"""Generate public/email/masthead.gif, the animated ornament band for the newsletter.

Frame 1 is the finished, static design: Outlook desktop shows only the first
frame, so it must stand on its own. Clients that animate GIFs then see a gold
glint sweep along the rules and through the khatam rosette, followed by a long
still hold. Re-run after changing the design:

    python3 scripts/generate-email-gif.py
"""

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "public" / "email" / "masthead.gif"

W, H = 1200, 160          # rendered size; the email displays it at 600x80
SS = 3                    # supersampling factor for smooth strokes
NAVY = (11, 22, 40)       # --navy, baked in: no transparency, so no jagged edges
GOLD = (201, 168, 76)     # --gold
GLINT = (246, 228, 170)   # pale gold highlight


def line_mask() -> Image.Image:
    """White-on-black mask of every gold stroke, drawn supersampled then reduced."""
    w, h, s = W * SS, H * SS, SS
    img = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(img)
    cx, cy = w / 2, h / 2
    stroke = round(2.2 * s)

    # Khatam rosette: two squares turned 45 degrees against each other, ringed
    half = 34 * s
    for angle in (0, 45):
        pts = []
        for corner in (45, 135, 225, 315):
            a = math.radians(corner + angle)
            pts.append((cx + half * math.sqrt(2) * math.cos(a), cy + half * math.sqrt(2) * math.sin(a)))
        d.line(pts + [pts[0]], fill=255, width=stroke, joint="curve")
    for r, wdt in ((15 * s, stroke), (56 * s, round(1.2 * s))):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=255, width=wdt)

    # Double rules running out from the rosette to the margins, with diamond terminals
    gap = 76 * s
    margin = 36 * s
    for dy in (-7 * s, 7 * s):
        y = cy + dy
        d.line((margin, y, cx - gap, y), fill=255, width=round(1.4 * s))
        d.line((cx + gap, y, w - margin, y), fill=255, width=round(1.4 * s))
    for x in (margin - 10 * s, w - margin + 10 * s):
        k = 7 * s
        d.polygon([(x, cy - k), (x + k, cy), (x, cy + k), (x - k, cy)], fill=255)

    return img.resize((W, H), Image.LANCZOS)


def band(center_x: float, width: float = 170) -> Image.Image:
    """Soft vertical band of light, 255 at center_x fading to 0."""
    row = [
        round(255 * math.exp(-((x - center_x) ** 2) / (2 * (width / 2.6) ** 2)))
        for x in range(W)
    ]
    strip = Image.new("L", (W, 1))
    strip.putdata(row)
    return strip.resize((W, H))


def frame(mask: Image.Image, glint_x: float | None) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY)
    img.paste(Image.new("RGB", (W, H), GOLD), mask=mask)
    if glint_x is not None:
        light = ImageChops.multiply(mask, band(glint_x))
        halo = light.filter(ImageFilter.GaussianBlur(3)).point(lambda v: v * 0.45)
        img.paste(Image.new("RGB", (W, H), GLINT), mask=ImageChops.lighter(light, halo))
    return img


def main() -> None:
    mask = line_mask()
    still = frame(mask, None)

    sweep_steps = 34
    sweep = [frame(mask, -200 + (W + 400) * i / (sweep_steps - 1)) for i in range(sweep_steps)]

    frames = [still] + sweep + [still]
    durations = [600] + [45] * sweep_steps + [5200]

    # One shared palette keeps the gold identical across frames and the file small
    palette_src = Image.new("RGB", (W, H * 2))
    palette_src.paste(still, (0, 0))
    palette_src.paste(sweep[sweep_steps // 2], (0, H))
    pal = palette_src.quantize(colors=48, method=Image.Quantize.MEDIANCUT)
    quantized = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    quantized[0].save(
        OUT,
        save_all=True,
        append_images=quantized[1:],
        duration=durations,
        loop=2,
        optimize=True,
        disposal=1,
    )
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB, {len(frames)} frames)")


if __name__ == "__main__":
    main()
