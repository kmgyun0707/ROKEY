"""Image preprocessing helpers (archived)."""
from PIL import Image
from pathlib import Path

def ensure_jpeg(path: str) -> str:
    p = Path(path)
    if p.suffix.lower() in {".jpg", ".jpeg"}:
        return str(p)
    im = Image.open(p)
    out = p.with_suffix(".jpg")
    im.convert("RGB").save(out, "JPEG", quality=90)
    return str(out)
