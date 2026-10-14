# 驗收

## 1. 硬性限制與健全性（必須全過）

- [ ] 每一頁轉場結束後，所有資訊完整可讀（沒有元素停在透明、裁切、位移的中間狀態）
- [ ] 靜止時文字本體不動；細微動態在 `motion-principles.md` 的上限內
- [ ] 快速連按翻頁、往回翻都不會錯亂
- [ ] 斷網／CDN 失效時內容仍完整顯示
- [ ] `prefers-reduced-motion: reduce` 時只剩淡入淡出
- [ ] 手機直向可等比縮放、可滑動翻頁；網址 `#n` 可直接開到第 n 頁
- [ ] 數據與事實正確（使用者提供的資料不擅自更動）

## 2. 作品集標準（誠實自評）

不是逐項打勾，而是用動態設計總監的眼光看自己的作品：

- 這份東西放進你的作品集，你敢嗎？
- 觀眾看完會記得哪一個畫面？如果答不出來，就是還缺一個「招牌時刻」。
- 哪一次轉場最平庸、最像套模板？重做它。
- 整份看起來像一支連續的影片，還是一張張換掉的幻燈片？

找到最弱的一處就修，修完再看一次。

## 截圖檢查（建議）

若環境有 Node，在暫存目錄執行：

```bash
npm i -D playwright && npx playwright install chromium
```

```js
// shot.mjs — node shot.mjs path/to/deck.html [--mid]
// 預設擷取每頁靜止狀態；加 --mid 另外擷取轉場過程中的影格，檢查動態編排
import { chromium } from "playwright";
const file = "file://" + new URL(process.argv[2], "file://" + process.cwd() + "/").pathname;
const mid = process.argv.includes("--mid");
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1600, height: 900 } });
await p.goto(file); await p.waitForTimeout(3000);
const n = await p.evaluate(() => window.Deck?.total ?? 1);
const id = i => String(i + 1).padStart(2, "0");
for (let i = 0; i < n; i++) {
  await p.evaluate(i => window.Deck.go(i), i);
  if (mid) for (const t of [150, 400, 750]) {           // 轉場開始後第 t ms
    await p.waitForTimeout(t - (t === 150 ? 0 : t === 400 ? 150 : 400));
    await p.screenshot({ path: `shot-${id(i)}-t${t}.png` });
  }
  await p.waitForFunction(() => !window.Deck.busy, null, { timeout: 10000 });
  await p.waitForTimeout(300);
  await p.screenshot({ path: `shot-${id(i)}.png` });
}
await b.close();
```

用 Read 工具檢視截圖：靜止圖檢查資訊完整與構圖；過程影格檢查轉場是否真的有編排、而不是一片空白或整頁淡入。

> WSL／無 sudo 環境若 Chromium 報 `libnspr4.so` 等缺函式庫：
> `apt-get download libnspr4 libnss3 libasound2t64 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libatspi2.0-0t64`，
> 逐一 `dpkg -x <deb> ./libs`，再以 `LD_LIBRARY_PATH=$PWD/libs/usr/lib/x86_64-linux-gnu node shot.mjs ...` 執行。
