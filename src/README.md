# 簡報建置

`csie-assembly-115.html` 是由這裡的模板和資料組出來的單一檔案。家長日簡報的頁面和老師照片都以 base64 的形式內嵌在裡面。

## 檔案
| 檔案 | 用途 |
|---|---|
| `deck.src.html` | 模板：樣式、手工頁面、轉場引擎。`<!--@@…@@-->` 是預留位置 |
| `build.py` | 教授資料（`PROFS`），用來產生引言卡、實驗室地圖、謝謝老師頁，並把圖片與 GSAP 填進模板 |
| `render.py` | 把家長日簡報 PDF 轉成 `build/` 下的頁面圖、照片和照片座標 |
| `vendor/` | GSAP 3.13 與 SplitText，內嵌進 HTML，斷網也能播放 |

## 重新產生
```bash
cd src
python -m venv .venv && . .venv/bin/activate   # 或使用 uv venv
pip install -r requirements.txt
python render.py      # 需要 ../docs/115學年度新生家長日-final.pdf.pdf
python build.py       # 輸出 ../csie-assembly-115.html
```

`build/` 是產物，不進版控。原始 PDF 也不進版控，請另外保存。

## 常見修改
- **教授資料、一句話介紹**：改 `build.py` 裡的 `PROFS`。順序必須和家長日簡報的頁序一致。
- **其他頁面文字、頒獎頁**：改 `deck.src.html`。
- **頒獎小隊與獎品**：不用重建，播放時按 `E` 設定即可。
