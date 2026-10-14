"""組裝「資工系期初系員大會」動態簡報（單一 HTML，可離線播放）。

usage:  python build.py [輸出路徑，預設 ../csie-assembly-2026.html]

需要：pymupdf pillow fonttools brotli（見 requirements.txt）
素材：../docs/115學年度新生家長日-final.pdf、../docs/分組名單.md、../docs/回饋表單qrcode.JPG
字型：.cache/NotoSansTC.ttf、.cache/JetBrainsMono.ttf（不存在時自動從 google/fonts 下載）
"""
import base64, html, io, json, random, re, sys, urllib.request
from pathlib import Path

import pymupdf
from PIL import Image
from fontTools import subset as ftsubset

D = Path(__file__).resolve().parent
DOCS = D.parent / "docs"
CACHE = D / ".cache"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else D.parent / "csie-assembly-2026.html"
PDF = DOCS / "115學年度新生家長日-final.pdf"
TEAMS_MD = DOCS / "分組名單.md"
QR_IMG = DOCS / "回饋表單qrcode.JPG"
FONTS = {
    "NotoSansTC.ttf": "https://github.com/google/fonts/raw/main/ofl/notosanstc/NotoSansTC%5Bwght%5D.ttf",
    "JetBrainsMono.ttf": "https://github.com/google/fonts/raw/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
}

esc = html.escape

# ---------------------------------------------------------------- 資料
# 順序 = 主持稿順序 = 家長日簡報順序（個人頁 = 第 2k 頁、實驗室頁 = 第 2k+1 頁）
# 職稱、兼任、實驗室、專長取自家長日簡報；「適合」取自主持稿每位老師的結尾句
F = {"sys": "系統整合", "net": "網路通訊", "sw": "軟體發展"}
PROFS = [
    ("陳仁德", "副教授", "兼資工系系主任", "sys", "數位晶片設計實驗室", "E112",
     ["數位系統設計", "影像處理晶片設計"], "對晶片設計有興趣的同學"),
    ("丁德榮", "教授", "", "net", "光纖網路最佳化實驗室", "E109",
     ["高速網路", "無線網路", "智慧物聯網", "演算法設計", "人工智慧", "網路安全"], "對演算法有興趣的同學"),
    ("伍朝欽", "教授", "兼工學院院長、工學院國際工程碩士學位學程主任", "sys", "平行與智慧計算實驗室", "E107",
     ["高效能計算", "智能資訊系統", "智慧計算"], "想玩 GPU、對平行運算有興趣的同學"),
    ("易昶霈", "教授", "", "sys", "電路實驗室 (一)(二)", "EB229 · EB223",
     ["超大型積體電路", "嵌入式系統", "專利侵權鑑定"], "對物聯網裝置有興趣的同學"),
    ("陳伯岳", "教授", "", "sw", "數位系統設計實驗室", "E106",
     ["VLSI 架構設計", "影像處理"], "對演算法與硬體同時有熱誠的同學"),
    ("張英超", "教授", "", "net", "無線與行動網路實驗室", "E114",
     ["無線網路", "無線行動網路", "物聯網", "無人機派遣"], "對網路、無人機有興趣的同學"),
    ("鄧德雋", "教授", "", "net", "無線通訊網路實驗室", "E111",
     ["B5G / Pre-6G", "Quality-of-Service", "Wireless Local Area Network"], "對 5G 與網路通訊有興趣的同學"),
    ("蕭如淵", "教授", "", "sw", "多媒體技術實驗室", "E115",
     ["數位影像處理", "多媒體系統", "演算法設計分析"], "對影像處理有興趣的同學"),
    ("施明毅", "副教授", "", "sw", "資料探勘實驗室", "E117",
     ["電子商務", "資料庫系統", "演算法", "資料探勘"], "想往資料分析發展的同學"),
    ("詹益禎", "副教授", "兼圖書與資訊處圖資長 · 資工四導師", "net", "網路協定實驗室", "E113",
     ["網路通訊協定", "無線網路", "物聯網系統", "網路管理"], "對物聯網有興趣的同學"),
    ("賴聯福", "副教授", "", "sw", "軟體工程實驗室", "E108",
     ["模糊查詢", "專家系統", "軟體工程", "知識管理"], "對軟體工程有興趣的同學"),
    ("張家濟", "副教授", "資工三導師", "sys", "嵌入式系統暨無線感測網路實驗室", "E116",
     ["低功耗嵌入式系統設計", "無線感測網路", "微核心嵌入式作業系統"], "對嵌入式系統有興趣的同學"),
    ("黃耀賢", "助理教授", "兼圖書與資訊處網路與資訊系統管理組組長 · 資工二導師", "sw", "醫學影像處理實驗室", "E118",
     ["醫學影像處理", "人工智慧", "機器學習", "電腦輔助系統"], "對 AI 醫療有興趣的同學"),
    ("陳勇志", "助理教授", "資工一導師", "net", "煉金實驗室", "E105",
     ["電子設計自動化 (EDA)", "人工智慧代理人 (Agentic AI)", "強化學習", "嵌入式 Linux", "無人機系統"], "對 AI 有興趣的同學"),
]
N = len(PROFS)
TEAM_NUM = ["一", "二", "三", "四"]


def read_teams():
    rows = [l.strip() for l in TEAMS_MD.read_text().splitlines() if l.strip().startswith("|")]
    cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
    head, body = cells[0], [r for r in cells[2:]]
    lead_at = next(i for i, r in enumerate(body) if all(c == "隊輔" for c in r))
    members, leads = body[:lead_at], body[lead_at + 1]
    teams = []
    for j, h in enumerate(head):
        teams.append({"key": h, "members": [r[j] for r in members], "lead": leads[j]})
    assert len(teams) == 4, head
    return teams


# ---------------------------------------------------------------- 素材
def render_pages():
    out = CACHE / "pages"
    out.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(PDF)
    for i, page in enumerate(doc):
        f = out / f"p{i + 1:02d}.webp"
        if f.exists() and f.stat().st_mtime > PDF.stat().st_mtime:
            continue
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1920 / page.rect.width, 1080 / page.rect.height))
        im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        if im.size != (1920, 1080):
            im = im.resize((1920, 1080), Image.LANCZOS)
        im.save(f, "WEBP", quality=84, method=6)
    return [out / f"p{i + 1:02d}.webp" for i in range(doc.page_count)]


def qr_matrix():
    """把 QR 圖片取樣成模組矩陣（41×41），用向量重畫，投影時更銳利。"""
    import numpy as np
    im = Image.open(QR_IMG).convert("L")
    a = np.array(im) < 128
    h = a.shape[0]
    sub = a[: int(h * 0.75)]              # 圖片下方是標題文字，不取樣
    ys, xs = np.where(sub)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    run = 0
    for x in range(x0, x1):               # 左上定位圖樣寬 = 7 模組
        if sub[y0 + 2, x]: run += 1
        else: break
    width = x1 - x0 + 1
    n = min(range(21, 178, 4), key=lambda k: abs(width / k * 7 - run))
    ms = width / n
    rows = ["".join("1" if sub[int(y0 + (j + .5) * ms), int(x0 + (i + .5) * ms)] else "0" for i in range(n))
            for j in range(n)]
    try:                                   # 有 zxing-cpp 就驗證重畫結果
        import zxingcpp
        orig = zxingcpp.read_barcodes(im)[0].text
        s, q = 10, 4
        big = Image.new("L", ((n + 2 * q) * s,) * 2, 255)
        for j, r in enumerate(rows):
            for i, c in enumerate(r):
                if c == "1":
                    big.paste(0, ((i + q) * s, (j + q) * s, (i + q + 1) * s, (j + q + 1) * s))
        again = zxingcpp.read_barcodes(big)[0].text
        assert again == orig, "QR 重畫後內容不一致"
        print("QR 驗證通過：", orig[:60], "…")
    except ImportError:
        print("（未安裝 zxing-cpp，略過 QR 驗證）")
    return rows


def qr_svg_path(rows):
    d = []
    for j, r in enumerate(rows):
        for m in re.finditer(r"1+", r):
            d.append(f"M{m.start()} {j}h{m.end() - m.start()}v1h-{m.end() - m.start()}z")
    return "".join(d)


def fetch_fonts():
    CACHE.mkdir(exist_ok=True)
    for name, url in FONTS.items():
        if not (CACHE / name).exists():
            print("下載字型", name)
            urllib.request.urlretrieve(url, CACHE / name)


def subset_font(src, chars, out):
    opts = ftsubset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt", "palt", "vpal", "locl", "tnum"]
    opts.name_IDs = []
    opts.notdef_outline = True
    font = ftsubset.load_font(str(src), opts)
    sub = ftsubset.Subsetter(opts)
    sub.populate(text=chars)
    sub.subset(font)
    cmap = font.getBestCmap()
    ftsubset.save_font(font, str(out), opts)
    return {c for c in chars if ord(c) in cmap}


def uri(p, mime):
    return f"data:{mime};base64," + base64.b64encode(Path(p).read_bytes()).decode()


# ---------------------------------------------------------------- 產生頁面
def check_svg():
    return '<svg class="ck" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5"/></svg>'


def prof_list(cur):
    li = []
    for i, p in enumerate(PROFS, 1):
        st = "done" if i < cur else ("cur" if i == cur else "")
        mark = '<i class="cd-cur"></i>' if i == cur else ""
        li.append(f'<li class="{st} f-{p[3]}">{mark}<b>{i:02d}</b><span>{p[0]}</span>{check_svg() if i < cur else ""}</li>')
    return "".join(li)


def build_profs(pages):
    out = []
    for i, (name, title, role, field, lab, room, skills, fit) in enumerate(PROFS, 1):
        k = f"{i:02d}"
        at = round(3 + (i - 1) * 56 / N, 1)
        chips = "".join(f"<span>{esc(s)}</span>" for s in skills)
        out.append(f'''
<section class="slide card f-{field}" id="s-c{k}" data-transition="stow" data-sec="talk" data-item="{k} {name}" data-at="{at}">
  <div class="cd-main">
    <p class="cd-kick"><span class="cd-idx"><b>{k}</b><i> / {N}</i></span><span class="cd-field">{F[field]}領域</span></p>
    <h2 class="cd-name"><span class="nm">{name}</span><small>{title}</small></h2>
    <p class="cd-role">{esc(role)}</p>
    <dl class="cd-meta">
      <div class="cd-lab"><dt>實驗室</dt><dd><b>{esc(lab)}</b><code>{esc(room)}</code></dd></div>
      <div class="cd-sk"><dt>專長</dt><dd class="chips">{chips}</dd></div>
      <div class="cd-fit"><dt>適合</dt><dd><em>→</em>{esc(fit)}</dd></div>
    </dl>
  </div>
  <div class="cd-list"><p class="cd-lh"><span>專題介紹</span><span>{i:02d}/{N}</span></p><ol>{prof_list(i)}</ol></div>
</section>''')
        pg = 2 * i
        out.append(f'''
<section class="slide pdf" id="s-p{pg:02d}" data-transition="render" data-bar="off" data-sec="talk" data-item="{k} {name}" data-at="{at}">
  <img src="@@PAGE{pg:02d}@@" alt="家長日簡報第 {pg + 30} 頁：{name} {title} 個人介紹" decoding="async"></section>''')
        if pg + 1 <= len(pages):
            out.append(f'''
<section class="slide pdf" id="s-p{pg + 1:02d}" data-transition="scan" data-bar="off" data-sec="talk" data-item="{k} {name}" data-at="{at}">
  <img src="@@PAGE{pg + 1:02d}@@" alt="家長日簡報第 {pg + 31} 頁：{esc(lab)}設備介紹" decoding="async"></section>''')
    return "".join(out)


def build_labs():
    cols = []
    for fk in ["sys", "net", "sw"]:
        rows = "".join(
            f'<li data-i="{i}"><p><code>{esc(p[5])}</code><span>{p[0]} {p[1]}</span></p><b>{esc(p[4])}</b></li>'
            for i, p in enumerate(PROFS) if p[3] == fk)
        cnt = sum(1 for p in PROFS if p[3] == fk)
        cols.append(f'<div class="lb-col f-{fk}"><h3><span>{F[fk]}領域</span><em>{cnt} 間</em></h3><ol>{rows}</ol></div>')
    return "".join(cols)


def build_flame():
    return "".join(f'<i class="fl-c f-{p[3]}" style="left:{i * 40}px">{p[0][0]}</i>' for i, p in enumerate(PROFS))


def build_teams(teams):
    cols = []
    for j, t in enumerate(teams):
        names = "".join(f"<li>{esc(m)}</li>" for m in t["members"])
        cols.append(f'''<div class="tm-col t{j + 1}"><p class="tm-no">TEAM 0{j + 1}</p><h3>第{TEAM_NUM[j]}小隊</h3>
      <ol>{names}</ol><p class="tm-lead"><span>隊輔</span><b>{esc(t["lead"])}</b></p></div>''')
    return "".join(cols)


def cutlet(seed):
    """雞排外形：扁平、邊緣酥脆凹凸的不規則形（決定性亂數）"""
    import math
    rnd = random.Random(seed)
    cx, cy, rx, ry, tilt = 380, 300, 310, 200, math.radians(-7)
    pts = []
    for i in range(120):
        t = i / 120 * math.tau
        k = 1 + .07 * math.sin(3 * t + 1) + .05 * math.sin(5 * t + 2.2) + .035 * math.sin(2 * t) + rnd.uniform(-.018, .022)
        x, y = math.cos(t) * rx * k, math.sin(t) * ry * k
        pts.append((cx + x * math.cos(tilt) - y * math.sin(tilt), cy + x * math.sin(tilt) + y * math.cos(tilt)))
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def crumbs(seed, n):
    """雞排麵衣的顆粒（決定性亂數）"""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(70, 690), rnd.uniform(90, 510)
        r = rnd.uniform(4, 11)
        c = rnd.choice(["#f9d47e", "#f3bf5a", "#c97a22", "#b5661a"])
        out.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r:.1f}" ry="{r * rnd.uniform(.6, 1):.1f}" fill="{c}"/>')
    return "".join(out)


def pebbles(seed):
    rnd = random.Random(seed)
    out = []
    cols, rws = 10, 5
    for j in range(rws):
        for i in range(cols):
            cx = 80 + i * 66 + rnd.uniform(-8, 8) + (16 if j % 2 else 0)
            cy = 90 + j * 66 + rnd.uniform(-6, 6)
            rx, ry = rnd.uniform(20, 27), rnd.uniform(15, 21)
            c = rnd.choice(["#e6e0d2", "#cfc8b8", "#a9a293", "#8c867a", "#d8b77c", "#b9c2c9"])
            rot = rnd.uniform(-40, 40)
            d = abs(i - (cols - 1) / 2) + abs(j - (rws - 1) / 2)
            out.append(
                f'<g data-d="{d:.2f}" transform="translate({cx:.0f} {cy:.0f}) rotate({rot:.0f})"><g class="pb">'
                f'<ellipse rx="{rx:.1f}" ry="{ry:.1f}" fill="{c}"/>'
                f'<ellipse cx="{-rx * .3:.1f}" cy="{-ry * .35:.1f}" rx="{rx * .38:.1f}" ry="{ry * .26:.1f}" fill="#fff" opacity=".45"/></g></g>')
    return "".join(out)


# ---------------------------------------------------------------- 組裝
def main():
    fetch_fonts()
    pages = render_pages()
    teams = read_teams()
    rows = qr_matrix()

    src = (D / "deck.html").read_text()
    src = src.replace("<!--@@PROFS@@-->", build_profs(pages))
    src = src.replace("<!--@@LABS@@-->", build_labs())
    src = src.replace("<!--@@FLAME@@-->", build_flame())
    src = src.replace("<!--@@TEAMS@@-->", build_teams(teams))
    src = src.replace("@@CUTLET@@", cutlet(11))
    src = src.replace("<!--@@CRUMBS@@-->", crumbs(7, 110))
    src = src.replace("<!--@@PEBBLES@@-->", pebbles(3))
    src = src.replace("@@QR_N@@", str(len(rows)))
    src = src.replace("@@QR_PATH@@", qr_svg_path(rows))
    src = src.replace("/*@@QR_ROWS@@*/", json.dumps(rows))
    src = src.replace("/*@@TEAMS_JSON@@*/", json.dumps(teams, ensure_ascii=False))
    src = src.replace("/*@@PROFS_JSON@@*/", json.dumps([{"name": p[0], "field": p[3]} for p in PROFS], ensure_ascii=False))
    left = [l.strip()[:90] for l in src.splitlines() if "@@" in l and not re.search(r"@@(PAGE\d\d|GSAP|FONTS)@@", l)]
    assert not left, left

    # 字型子集：涵蓋整份 HTML 用到的所有字元（含 JS 字串）
    chars = set(src) | set(" 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    chars = "".join(sorted(c for c in chars if ord(c) >= 32))
    tc = subset_font(CACHE / "NotoSansTC.ttf", chars, CACHE / "ntc.woff2")
    jb = subset_font(CACHE / "JetBrainsMono.ttf", chars, CACHE / "jbm.woff2")
    missing = [c for c in chars if c not in tc and c not in jb and ord(c) > 127]
    if missing:
        print("兩套字型都沒有的字元（會用系統字型）：", "".join(missing))
    fonts = (
        f'@font-face{{font-family:"NTC";src:url({uri(CACHE / "ntc.woff2", "font/woff2")}) format("woff2");font-weight:100 900;font-display:block}}\n'
        f'@font-face{{font-family:"JBM";src:url({uri(CACHE / "jbm.woff2", "font/woff2")}) format("woff2");font-weight:100 800;font-display:block}}\n'
    )
    src = src.replace("/*@@FONTS@@*/", fonts)
    for i, p in enumerate(pages, 1):
        src = src.replace(f"@@PAGE{i:02d}@@", uri(p, "image/webp"))
    src = src.replace("/*@@GSAP@@*/", (D / "vendor" / "gsap.min.js").read_text())
    OUT.write_text(src)
    kb = lambda p: (CACHE / p).stat().st_size // 1024
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.2f} MB（字型 {kb('ntc.woff2')} KB + {kb('jbm.woff2')} KB）")


if __name__ == "__main__":
    main()
