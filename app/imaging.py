"""Pictures kept inside the app (receipts, note pictures): shrunk to a small JPEG so the database and backups stay light.
The original file on the phone is not needed afterwards - the copy lives in the app."""
import base64
import io
import os

from .repo import AppError

EXTENSIONS = ["jpg", "jpeg", "png", "webp", "gif", "heic"]
MAX_SIDE = 1280          # longest side in pixels
QUALITY = 70
MAX_INPUT = 30 * 1024 * 1024
MAX_RAW = 1500 * 1024    # without Pillow the file is stored as is, so it must already be small


def compress_bytes(raw: bytes) -> bytes:
    """JPEG, longest side <= MAX_SIDE. Needs Pillow; raises ImportError/OSError otherwise."""
    from PIL import Image, ImageOps
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    else:
        img = img.convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=QUALITY, optimize=True)
    return out.getvalue()


def load(path: str) -> str:
    """Image file -> base64 text of a small JPEG. Raises AppError for unsupported / unreadable files."""
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    if ext not in EXTENSIONS:
        raise AppError("نوع الصورة غير مدعوم (jpg, png, webp)")
    size = os.path.getsize(path)
    if size > MAX_INPUT:
        raise AppError("الصورة كبيرة جداً")
    with open(path, "rb") as f:
        raw = f.read()
    try:
        data = compress_bytes(raw)
    except ImportError:                      # Pillow missing in this build: keep the file only if it is already small
        if size > MAX_RAW:
            raise AppError("الصورة كبيرة (الحد 1.5 ميغا). صغّرها وجرب مرة ثانية")
        data = raw
    except Exception:
        raise AppError("ما كدرت أقرأ الصورة")
    return base64.b64encode(data).decode("ascii")


def to_bytes(b64: str) -> bytes:
    return base64.b64decode(b64)


def guess_ext(b64: str) -> str:
    head = to_bytes(b64[:32])
    if head.startswith(b"\x89PNG"):
        return "png"
    if head[:4] == b"RIFF":
        return "webp"
    if head[:3] == b"GIF":
        return "gif"
    return "jpg"
