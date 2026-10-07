"""組裝資工系期初系員大會簡報（單一 HTML）。
先執行 render.py 產生 build/ 圖片，再執行本檔。
usage: python build.py [輸出路徑，預設 ../csie-assembly-115.html]
"""
import base64, html, json, sys
from pathlib import Path

D = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else D.parent / "csie-assembly-115.html"
B = D / "build"
if not (B / "photos.json").exists():
    sys.exit("找不到 build/photos.json，請先執行：python render.py")

def uri(p, mime="image/webp"):
    return f"data:{mime};base64," + base64.b64encode(Path(p).read_bytes()).decode()

PH = json.load(open(B / "photos.json"))

# 簡報順序 = 主持稿順序 = 家長日簡報順序
# (姓名, 職稱(依家長日簡報), 兼任/導師, 領域, 實驗室, 實驗室教室, 研究室, 專長[], 一句話, 推薦給)
PROFS = [
    ("陳仁德", "副教授", "兼資工系系主任", "系統整合", "數位晶片設計實驗室", "E112", "E231",
     ["數位系統設計", "影像處理晶片設計"],
     "把演算法，<br>變成一顆電路。", "對硬體、晶片設計有興趣的你"),
    ("丁德榮", "教授", "", "網路通訊", "光纖網路最佳化實驗室", "E109", "E237",
     ["高速網路", "無線網路", "智慧物聯網", "演算法設計", "人工智慧", "網路安全"],
     "資料怎麼用最短的時間、<br>最省的資源送到你手上？", "喜歡演算法題，又想用在真實系統上的你"),
    ("伍朝欽", "教授", "兼工學院院長、工學院國際工程碩士學位學程主任", "系統整合", "平行與智慧計算實驗室", "E107", "E140",
     ["高效能計算", "智能資訊系統", "智慧計算"],
     "計算量超大的程式，<br>要怎麼加速？", "想玩 GPU、對平行運算有興趣的你"),
    ("易昶霈", "教授", "", "系統整合", "電路實驗室", "EB229・EB223", "E134",
     ["超大型積體電路", "嵌入式系統", "專利侵權鑑定"],
     "從麵包板，一路做到<br>能連網的裝置。", "對物聯網裝置有興趣的你"),
    ("陳伯岳", "教授", "", "軟體發展", "數位系統設計實驗室", "E106", "E232",
     ["VLSI 架構設計", "影像處理"],
     "替影像演算法，<br>設計專屬的硬體。", "演算法與硬體都想碰的你"),
    ("張英超", "教授", "", "網路通訊", "無線與行動網路實驗室", "E114", "E136",
     ["無線網路", "無線行動網路", "物聯網", "無人機派遣"],
     "用 AI 辨識機車駛入<br>大車盲點，主動預警。", "對網路、無人機有興趣的你"),
    ("鄧德雋", "教授", "", "網路通訊", "無線通訊網路實驗室", "E111", "E236",
     ["B5G / Pre-6G", "Quality-of-Service", "Wireless LAN"],
     "5G 之後呢？<br>下一代網路已經在路上。", "對 5G 與網路通訊有興趣的你"),
    ("蕭如淵", "教授", "", "軟體發展", "多媒體技術實驗室", "E115", "E135",
     ["數位影像處理", "多媒體系統", "演算法設計分析"],
     "拍照、修圖、影片壓縮，<br>背後都是演算法。", "對影像處理有興趣的你"),
    ("施明毅", "副教授", "", "軟體發展", "資料探勘實驗室", "E117", "E138",
     ["電子商務", "資料庫系統", "演算法", "資料探勘"],
     "從大量資料裡，<br>找出規則與趨勢。", "想往資料分析、資料工程發展的你"),
    ("詹益禎", "副教授", "兼圖書與資訊處圖資長・資工四導師", "網路通訊", "網路協定實驗室", "E113", "E234",
     ["網路通訊協定", "無線網路", "物聯網系統", "網路管理"],
     "把網路理論，<br>做成真正的裝置。", "對物聯網有興趣的你"),
    ("賴聯福", "副教授", "", "軟體發展", "軟體工程實驗室", "E108", "E139",
     ["軟體工程", "知識管理", "專家系統", "模糊查詢"],
     "讓一群人把軟體做好，<br>還能長期維護。", "想做 App、完整做一個軟體專案的你"),
    ("張家濟", "副教授", "資工三導師", "系統整合", "嵌入式系統暨無線感測網路實驗室", "E116", "E234",
     ["低功耗嵌入式系統設計", "無線感測網路", "微核心嵌入式作業系統"],
     "感測器在野外幾個月沒人換電池，<br>省電是一門學問。", "對嵌入式系統有興趣的你"),
    ("黃耀賢", "助理教授", "兼圖資處網路與資訊系統管理組組長・資工二導師", "軟體發展", "醫學影像處理實驗室", "E118", "E233",
     ["醫學影像處理", "人工智慧", "機器學習", "電腦輔助系統"],
     "用 AI 協助醫師：<br>乳癌輔助診斷、肺結節偵測。", "對 AI 醫療有興趣的你"),
    ("陳勇志", "助理教授", "資工一導師", "網路通訊", "煉金實驗室", "E105", "E235",
     ["電子設計自動化 EDA", "Agentic AI", "強化學習", "嵌入式 Linux", "無人機系統"],
     "資工的盡頭，<br>是煉金？", "對 AI 代理人、EDA 有興趣的你"),
]
N = len(PROFS)
DOMAIN_EN = {"系統整合": "SYSTEMS", "網路通訊": "NETWORKS", "軟體發展": "SOFTWARE"}

PH_H = 600          # 卡片上照片高度
PH_TOP = 150
PH_RIGHT = 1760

slides, css, vars_ = [], [], []
for i, (name, title, role, dom, lab, labroom, office, skills, hook, forwho) in enumerate(PROFS, 1):
    k = f"{i:02d}"
    pg = 2 * i                       # 家長日簡報頁碼（個人頁）
    tx, ty, tw, th = PH[f"p{pg:02d}"]
    w = round(PH_H * tw / th, 1)
    left = PH_RIGHT - w
    vars_.append(f"--ph{k}:url({uri(B / 'photos' / f'p{pg:02d}.webp')});")
    css.append(f"#s-c{k} .ph{{left:{left}px;width:{w}px;background-image:var(--ph{k})}}"
               f"#s-c{k} .ph-cap{{left:{left}px;width:{w}px}}"
               f"#s-c{k} .c-body{{width:{left - 160 - 90}px}}")
    chips = "".join(f"<li>{html.escape(s)}</li>" for s in skills)
    role_html = f'<span class="role">{html.escape(role)}</span>' if role else ""
    slides.append(f'''
  <!-- {k} {name}：主持人引言卡 → 交棒給原簡報個人頁（照片共享元素） -->
  <section class="slide card" id="s-c{k}" data-stage="1" data-transition="wipe" data-title="{name} · 引言"
           data-target="{tx},{ty},{tw},{th}">
    <div class="c-ghost" aria-hidden="true">{k}</div>
    <div class="c-body">
      <p class="c-kick" data-a="fade"><b>LAB {k}</b><i>/ {N:02d}</i><span class="tag">{dom}領域 · {DOMAIN_EN[dom]}</span></p>
      <h2 class="c-name" data-a="mask"><span class="ln"><span>{name}</span></span><small>{title}</small></h2>
      <p class="c-role" data-a="fade">{role_html or '&nbsp;'}</p>
      <p class="c-hook" data-a="chars">{hook}</p>
      <div class="c-meta">
        <p class="c-lab" data-a="rise"><em>LAB</em><span>{html.escape(lab)}</span><b>{labroom}</b></p>
        <div class="c-skills"><em>專長</em><ul data-a="chips">{chips}</ul></div>
        <p class="c-for" data-a="fade"><em>→</em>推薦給：{html.escape(forwho)}</p>
      </div>
    </div>
    <div class="ph" role="img" aria-label="{name}"></div>
    <p class="ph-cap" data-a="fade"><span>OFFICE {office}</span><span>{name} {title}</span></p>
  </section>
  <section class="slide embed" id="s-p{pg:02d}" data-stage="1" data-rail="off" data-transition="handoff"
           data-title="{name} · 原簡報 P.{pg + 30}"><img src="@@PAGE{pg:02d}@@" alt="{name} {title} 介紹頁（家長日簡報 P.{pg + 30}）" decoding="async"></section>''')
    if pg + 1 <= 28:
        slides.append(f'''
  <section class="slide embed" id="s-p{pg + 1:02d}" data-stage="1" data-rail="off" data-transition="scan"
           data-title="{name} · 實驗室 P.{pg + 31}"><img src="@@PAGE{pg + 1:02d}@@" alt="{html.escape(lab)} 設備介紹（家長日簡報 P.{pg + 31}）" decoding="async"></section>''')

# 14 間實驗室地圖（依領域分欄，編號 = 出場順序）
cols = {}
for i, p in enumerate(PROFS, 1):
    cols.setdefault(p[3], []).append((i, p))
labmap = []
for dom in ["系統整合", "網路通訊", "軟體發展"]:
    rows = "".join(
        f'<li><b>{i:02d}</b><span>{html.escape(p[4])}</span><i>{p[0]}・{p[5]}</i></li>' for i, p in cols[dom])
    labmap.append(f'<div class="lm-col" data-a="col"><h3><span>{dom}領域</span><em>{DOMAIN_EN[dom]} · {len(cols[dom])}</em></h3><ol>{rows}</ol></div>')

recap = "".join(
    f'<li><i style="background-image:var(--ph{i:02d})"></i><span>{p[0]}</span></li>' for i, p in enumerate(PROFS, 1))

# 頒獎粒子：決定性亂數，靜止狀態即散落位置
import random
rnd = random.Random(7)
def burst(n, cx, cy):
    out = []
    for _ in range(n):
        x = rnd.uniform(60, 1860); y = rnd.uniform(60, 900)
        if abs(x - cx) < 260 and abs(y - cy) < 260: x += 520 * (1 if x >= cx else -1)
        s = rnd.choice(["sq", "ci", "ln"]); r = rnd.randint(0, 180); z = rnd.uniform(.6, 1.4)
        out.append(f'<i class="{s}" style="left:{x:.0f}px;top:{y:.0f}px;--r:{r}deg;--z:{z:.2f}"></i>')
    return '<div class="burst" aria-hidden="true" data-cx="%d" data-cy="%d">%s</div>' % (cx, cy, "".join(out))

src = (D / "deck.src.html").read_text()
src = src.replace("<!--@@PROFS@@-->", "".join(slides))
src = src.replace("<!--@@LABMAP@@-->", "".join(labmap))
src = src.replace("<!--@@RECAP@@-->", recap)
src = src.replace("/*@@PROF_CSS@@*/", "\n".join(css))
src = src.replace("/*@@PHOTO_VARS@@*/", "\n".join(vars_))
for tag in ["r3", "r2", "r1", "sp", "r1p"]:
    src = src.replace(f"<!--@@BURST_{tag}@@-->", burst(34 if tag != "r1p" else 46, 380 if tag != "r1p" else 960, 470))
for n in range(1, 29):
    src = src.replace(f"@@PAGE{n:02d}@@", uri(B / "pages" / f"p{n:02d}.webp"))
left = [l.strip()[:80] for l in src.splitlines() if "@@" in l and "@@GSAP@@" not in l and "@@SPLIT@@" not in l]
assert not left, left
src = src.replace("/*@@GSAP@@*/", (D / "vendor" / "gsap.min.js").read_text())
src = src.replace("/*@@SPLIT@@*/", (D / "vendor" / "SplitText.min.js").read_text())
OUT.write_text(src)
print(OUT, f"{OUT.stat().st_size / 1e6:.2f} MB")
