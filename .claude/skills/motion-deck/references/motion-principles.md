# 動態設計準則

## 1. 時間與節奏

- 定義一個 **beat**（建議 0.08–0.12s），所有延遲與 stagger 都是 beat 的倍數，節奏才會一致。
- 轉場總長：**0.9–1.8s**。太短像切換，太長會讓翻頁者不耐。
- 退場比進場短（約 0.6 倍）：觀眾關心的是「接下來是什麼」。
- **重疊（overlap）**：下一頁進場在上一頁退場完成前 30–50% 就開始，避免「空白一拍」。
- 進場順序依資訊層級：視覺錨點 → 標題 → 主要內容 → 次要資訊 → 裝飾。

## 2. 緩動曲線（不要用預設值）

| 用途 | 建議 |
|---|---|
| 主要進場（抵達、落定） | `expo.out`、`power4.out`、`cubic-bezier(0.16, 1, 0.3, 1)` |
| 退場（離開、加速） | `power3.in`、`cubic-bezier(0.7, 0, 0.84, 0)` |
| 畫面級移動（鏡頭、遮罩） | `expo.inOut`、`cubic-bezier(0.87, 0, 0.13, 1)` |
| 彈性強調（少量使用） | `back.out(1.6)`、`elastic.out(1, 0.5)` |
| 細微動態 | `sine.inOut`，yoyo 循環 |

整份簡報選 **一條主曲線** 作為簽名，其餘為輔助。

## 3. 轉場手法庫（混用，但共享母題）

- **遮罩揭露**：`clip-path: inset()/circle()/polygon()` 從某方向擦入；可用幾何形狀呼應主視覺。
- **分層視差**：背景、中景、前景以不同速度與距離位移，創造深度。
- **共享元素變形**：上一頁的某個形狀／數字／線條，透過 GSAP Flip 或 MorphSVG 成為下一頁的元素。
- **文字編排**：SplitText 拆成字／詞／行，以遮罩行（line mask）、逐字錯位、模糊聚焦進場。
- **鏡頭運動**：整個舞台 scale + translate，像攝影機推近進入下一頁的細節。
- **數字滾動**：數據從 0 計數到目標值（結束時必須顯示精確的最終值）。
- **線條繪製**：SVG `stroke-dashoffset` 描繪圖表、路徑、框線。
- **色塊擦除（wipe）**：一層或多層色塊依序掃過畫面，在色塊後方換頁。
- **粒子聚合**：粒子從散亂狀態聚合成形狀或文字，再讓真實 DOM 文字接手。

## 4. 編排（choreography）技巧

- **Stagger 要有方向**：從視覺焦點向外、沿著閱讀方向，或依網格的對角線。用 `stagger: { each, from: "center" | "start" | [x,y] }`。
- **預備動作（anticipation）**：大動作前加一個小的反向動作（例如先縮 2% 再推出）。
- **跟隨與延遲（follow-through）**：主體停下後，附屬元素晚 1–2 beat 才落定。
- **不同屬性錯開**：位移先到、透明度略早完成、模糊最後消失，讓動作有質感。
- **大小對比**：一頁之中只有一個「主角動作」，其他元素配合，不要全部同等搶戲。

## 5. 細微動態（靜止狀態）規範

| 屬性 | 上限 |
|---|---|
| 位移 | ≤ 6px（背景裝飾可到 20px，但速度要極慢） |
| 縮放 | ≤ 1.5% |
| 透明度變化 | ≤ 0.15 |
| 旋轉 | ≤ 2°，或背景元素的極慢自轉（≥ 40s 一圈） |
| 週期 | 4–14s，多個元素週期互質，避免同步律動 |

- **允許**：背景漸層流動、光暈呼吸、粒子漂移、網格線微光、裝飾線的流光、滑鼠視差（≤ 10px）。
- **禁止**：文字本體持續移動、閃爍、跑馬燈；任何會吸走閱讀注意力的高對比變化。
- 轉場期間暫停細微動態，轉場結束後再淡入（避免動態疊加混亂）。

## 6. 視覺系統

- **舞台**：固定 1920×1080 設計座標，再等比縮放到視窗，構圖才精確。
- **字體**：標題用有個性的字體（顯示體），內文用高可讀性字體；中文推薦 Noto Sans TC / Noto Serif TC，搭配英文顯示字體（如 Space Grotesk、Fraunces、Syne、Instrument Serif）。
- **字級**：標題 96–180px，內文 28–40px（1920 寬座標）。資訊量大的頁面可縮小內文，但仍要在投影時清楚可讀。
- **色彩**：一個主色、一個強調色、深淺背景各一，對比度至少 4.5:1。
- **構圖**：善用大留白、出血（元素超出畫面）、不對稱、網格對齊。每頁構圖應有變化，避免全部置中。

## 7. GSAP 實作片段

```js
// 遮罩行進場
const split = SplitText.create(el.querySelector("h1"), { type: "lines,words", mask: "lines" });
tl.from(split.words, { yPercent: 110, duration: 1, ease: "expo.out", stagger: 0.04 });

// 共享元素（Flip）
const state = Flip.getState(shared);
nextSlot.appendChild(shared);
Flip.from(state, { duration: 1.2, ease: "expo.inOut" });

// 數字滾動（結束時顯示精確值）
const obj = { v: 0 };
tl.to(obj, { v: target, duration: 1.4, ease: "power3.out",
  onUpdate: () => (num.textContent = Math.round(obj.v).toLocaleString()) });

// 細微動態
gsap.to(glow, { scale: 1.015, opacity: "-=0.1", duration: 6, ease: "sine.inOut", yoyo: true, repeat: -1 });
```

注意：SplitText 在轉場結束後若需要恢復原狀，可呼叫 `split.revert()`，確保靜止狀態的 DOM 乾淨。
