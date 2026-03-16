from __future__ import annotations

from pathlib import Path

from PIL import Image


def make_logo_mark(
    src: Path,
    dst: Path,
    *,
    crop_height_ratio: float = 0.70,
    bg_threshold: int = 18,
    pad_px: int = 40,
    max_side_px: int = 420,
) -> None:
    img = Image.open(src).convert("RGBA")
    w, h = img.size

    # Crop away the bottom caption area.
    crop = img.crop((0, 0, w, int(h * crop_height_ratio)))

    # Make near-black background transparent.
    pix = crop.load()
    for y in range(crop.size[1]):
        for x in range(crop.size[0]):
            r, g, b, a = pix[x, y]
            if r < bg_threshold and g < bg_threshold and b < bg_threshold:
                pix[x, y] = (r, g, b, 0)

    # Trim transparent borders.
    bbox = crop.getbbox()
    if bbox:
        crop = crop.crop(bbox)

    # Add padding.
    out = Image.new(
        "RGBA",
        (crop.size[0] + pad_px * 2, crop.size[1] + pad_px * 2),
        (0, 0, 0, 0),
    )
    out.paste(crop, (pad_px, pad_px))

    # Downscale to a consistent UI footprint.
    scale = min(max_side_px / out.size[0], max_side_px / out.size[1], 1.0)
    if scale < 1.0:
        out = out.resize(
            (int(out.size[0] * scale), int(out.size[1] * scale)),
            Image.LANCZOS,
        )

    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst)


if __name__ == "__main__":
    src = Path(r"d:\UPI-Hackathon-2\UPI-ai-agent\aicode\fast.jpg")
    dst = Path(r"d:\UPI-Hackathon-2\UPI-ai-agent\aicode\frontend\src\assets\fast-logo-mark.png")
    make_logo_mark(src, dst)
    print(f"Wrote {dst}")
