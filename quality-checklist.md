# 驗收清單

## 硬性限制
- [ ] 每一頁轉場結束後，所有資訊完整可讀（沒有元素停在透明、裁切、位移的中間狀態）
- [ ] 靜止時文字本體不動；細微動態符合 `motion-principles.md` 第 5 節上限
- [ ] 每次換頁都有轉場動畫，且手法有變化

## 動態品質
- [ ] 有明確的主緩動曲線與 beat，節奏一致
- [ ] 至少一次跨頁元素延續（共享元素／變形）
- [ ] 進場順序符合資訊層級，每頁只有一個主角動作
- [ ] 快速連按翻頁不會錯亂（轉場鎖或可中斷的 timeline）
- [ ] 往回翻頁也有合理的轉場（可用反向或鏡像版本）

## 健全性
- [ ] 斷網／CDN 失效時，內容仍完整顯示（預設狀態即靜止狀態）
- [ ] `prefers-reduced-motion: reduce` 時只用淡入淡出，細微動態關閉
- [ ] 手機直向時舞台等比縮放、不出現橫向捲軸；可滑動翻頁
- [ ] 網址 `#n` 可直接開啟第 n 頁，重新整理後停在同一頁

## 內容
- [ ] 語氣與資訊密度符合對象
- [ ] 字級在投影時清楚
- [ ] 數據與事實正確（使用者提供資料時，不擅自更動）

## 自動截圖檢查（選用）

若環境有 Node，在暫存目錄執行：

```bash
npm i -D playwright && npx playwright install chromium
```

```js
// shot.mjs — node shot.mjs path/to/deck.html
import { chromium } from "playwright";
const file = "file://" + new URL(process.argv[2], "file://" + process.cwd() + "/").pathname;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1600, height: 900 } });
await p.goto(file); await p.waitForTimeout(2500);
const n = await p.evaluate(() => window.Deck?.total ?? 1);
for (let i = 0; i < n; i++) {
  await p.evaluate(i => window.Deck.go(i), i);
  await p.waitForTimeout(2500);               // 等轉場結束
  await p.screenshot({ path: `shot-${String(i + 1).padStart(2, "0")}.png` });
}
await b.close();
```

用 Read 工具檢視截圖，確認每頁的靜止狀態完整、構圖平衡。

> WSL／無 sudo 環境若 Chromium 報 `libnspr4.so` 等缺函式庫：
> `apt-get download libnspr4 libnss3 libasound2t64 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libatspi2.0-0t64`，
> 逐一 `dpkg -x <deb> ./libs`，再以 `LD_LIBRARY_PATH=$PWD/libs/usr/lib/x86_64-linux-gnu node shot.mjs ...` 執行。
