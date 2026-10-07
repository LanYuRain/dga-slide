"""把家長日簡報 PDF 轉成簡報要用的圖片。
- build/pages/pNN.webp：每頁 1920×1080
- build/photos/pNN.webp：個人頁（偶數頁）上的老師照片，與頁面像素一致（供照片交棒轉場）
- build/photos.json：照片在 1920×1080 座標中的位置 [x, y, w, h]
usage: python render.py [PDF 路徑，預設 ../docs/115學年度新生家長日-final.pdf.pdf]
"""
import io, json, sys
from pathlib import Path
import pymupdf
from PIL import Image

D = Path(__file__).resolve().parent
PDF = Path(sys.argv[1]) if len(sys.argv) > 1 else D.parent / "docs" / "115學年度新生家長日-final.pdf.pdf"
B = D / "build"
(B / "pages").mkdir(parents=True, exist_ok=True)
(B / "photos").mkdir(parents=True, exist_ok=True)

doc = pymupdf.open(PDF)
meta = {}
for i, page in enumerate(doc):
    n = i + 1
    pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB").resize((1920, 1080), Image.LANCZOS)
    im.save(B / "pages" / f"p{n:02d}.webp", "WEBP", quality=80, method=6)
    if n >= 2 and n % 2 == 0:  # 個人頁：照片位於右半部下方
        infos = [x for x in page.get_image_info(xrefs=True) if x["bbox"][1] >= 220 and x["bbox"][0] > 560]
        r = pymupdf.Rect(infos[-1]["bbox"])
        pp = page.get_pixmap(matrix=pymupdf.Matrix(3, 3), clip=r)
        Image.open(io.BytesIO(pp.tobytes("png"))).convert("RGB").save(B / "photos" / f"p{n:02d}.webp", "WEBP", quality=84, method=6)
        meta[f"p{n:02d}"] = [round(v * 2, 1) for v in (r.x0, r.y0, r.width, r.height)]
(B / "photos.json").write_text(json.dumps(meta))
print(f"{doc.page_count} 頁 → {B}")
