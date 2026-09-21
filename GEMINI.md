# GEMINI.md - Listenfy 傾聽超能力探索 網站技術架構與開發規範

## 1. 專案概述與定位

* **專案名稱**：Listenfy 傾聽超能力探索

* **定位目標**：聆聽者培力計畫的前導自我覺察工具／推廣頁面。面向新加入學員與社會大眾，非給予評分的臨床診斷，而是一面呈現日常陪伴姿態與直覺溫度的溫柔小鏡子。

* **流程閉環**：

  1. 著陸頁（大標題 + 引導彈窗）

  2. 8 題動態打亂的 5 點量表探索

  3. 即時落點動畫與結果解析（象限圖 + 風格解析 + 羅盤意涵）

  4. 截圖/文字複製分享

  5. 導流填寫「學員表單（Google Form）」完成報名與分群。

## 2. 核心架構與技術選型

為確保輕量、易維護、零伺服器維護成本，採用 **單一檔案純靜態前端架構（Single Page Application / Vanilla Web）**：

* **核心技術**：HTML5 + Vanilla JavaScript（ES6+）+ Tailwind CSS（CDN 引入）

* **資料驅動**：無後端（Serverless）。題庫與四種風格資料直接以 JavaScript 內部物件陣列儲存，不需外部資料庫。

* **狀態管理**：純客戶端記憶體狀態（Runtime State）。不強制使用 LocalStorage，支援使用者一鍵「重新測驗」重設狀態。

* **外掛庫依賴（極簡）**：

  * `html2canvas`（用於生成結果分享圖卡）

  * Google Fonts：`Plus Jakarta Sans`（英數字）+ `Noto Sans TC`（繁體中文）

## 3. 視覺設計與 UI/UX 規範（嚴格遵守反 AI 樣板原則）

### 3.1 品牌專屬色系（Palette）

```
:root {
  --color-bg: #fffaed;        /* 底色：奶油米白，營造放鬆安心的對話氛圍 */
  --color-primary-orange: #ff7d59; /* 主色：珊瑚暖橘 */
  --color-primary-blue: #8fadff;   /* 主色：晴空澄藍 */
  --color-accent-green: #d9de81;   /* 輔色：芥綠 */
  --color-accent-yellow: #ffde94;  /* 輔色：柔暖黃 */
  --color-accent-pink: #f4a7c3;    /* 輔色：櫻粉 */
  --color-navy: #262f6b;           /* 文字與結構深色：深謐海軍藍 */
  --color-text-dark: #2c3345;      /* 內文主要色 */
  --color-text-muted: #6b7280;     /* 次要說明文字 */
}

```

### 3.2 視覺去樣板化（Anti-Generic UI Rules）

* **禁止過度使用卡片（Avoid Card Overload）**：

  * 避免千篇一律的「外框 + 投影 + 白底」方塊堆疊。

  * 改以大面積留白、柔和的色塊過渡、微弱的背景色差（如 `#fffaed` 與半透明白色遮罩）來進行視覺區塊劃分。

* **少用膠囊標籤（Minimize Badges）**：

  * 避免處處貼滿「類型 A」、「維度」等強烈裝飾性膠囊徽章。

  * 資訊分類透過排版層級（字級大小、字重 `font-black`、字距、局部色彩強調）清晰傳遞。

* **有機形態與圓角（Organic Shapes）**：

  * 呼應 Listenfy Logo 的水滴形雙子意象，使用非對稱圓角（如 `border-radius: 32px 20px 36px 24px` 或有機 Blob 造型）。

### 3.3 響應式佈局規範（RWD Guidelines）

* **移動端優先（Mobile-First）**：

  * 主容器：`w-full max-w-2xl mx-auto px-4 sm:px-6`，保證手機瀏覽時邊距舒適。

  * 選項按鈕：觸控目標高度保持在至少 `48px` 以上，上下間距緊湊有序（`gap-3`），點擊反饋（`active:scale-[0.99]`）迅速。

  * 象限矩陣圖：在手機直式螢幕下採用等比例縮放（`aspect-square` 或 `aspect-[4/3]`），圖表內部文字與座標點自動配合螢幕等比縮放，避免破版橫向滾動。

## 4. 題庫與隨機化邏輯（Questionnaire Engine）

### 4.1 原始題庫結構（8 題標準定義）

```
const rawQuestions = [
  // 焦點取向：情緒 (Emotion, E)
  {
    id: 'Q1',
    dimension: 'E',
    text: '當身邊朋友帶著混亂前來訴苦時，比起急著搞清楚整件事的前因後果，我會直覺先留意他話語裡的委屈、呼吸節奏與低落的眼神。'
  },
  {
    id: 'Q2',
    dimension: 'E',
    text: '平時聽朋友吐露心事時，我認為「如實反映對方的情感、讓他感覺被深刻理解與接納」，遠比「幫他找出理性盲點或分析解法」更能帶來安慰。'
  },
  // 焦點取向：事務 (Task, T)
  {
    id: 'Q3',
    dimension: 'T',
    text: '聽身邊的人分享卡關的難題時（如人際摩擦、課業瓶頸或職場壓力），我的大腦會自動開始梳理事件的因果關係，想找出問題真正的癥結點。'
  },
  {
    id: 'Q4',
    dimension: 'T',
    text: '對我而言，陪伴他人時最實質的幫助，是協助他把一團混亂的思緒整理出清晰架構，看清接下來有哪些具體可行的應對方向。'
  },
  // 關係姿態：培育 (Nurturing, N)
  {
    id: 'Q5',
    dimension: 'N',
    text: '當對方陷入情緒低潮或在原地打轉時，我很能涵容對話中的安靜與停頓，願意給出充分的留白，相信他有自己的復原節奏，不急著替他決定方向。'
  },
  {
    id: 'Q6',
    dimension: 'N',
    text: '面對朋友的人生困擾，我習慣如鏡子般反映他的話語、陪他慢慢看清想法，將主導權與選擇權完整留給對方，不過度介入他的生命決定。'
  },
  // 關係姿態：督促 (Coaching, C)
  {
    id: 'Q7',
    dimension: 'C',
    text: '當朋友反覆陷入同一個抱怨循環走不出來時，比起一味安慰，我更傾向溫和但直接地點出核心盲點，激發他面對現實卡點。'
  },
  {
    id: 'Q8',
    dimension: 'C',
    text: '在一次深入的聊心尾聲，我習慣和對方一起聚焦具體目標，列出一兩個踏實的小行動，並真誠期待他能在生活裡跨出這一步。'
  }
];

```

### 4.2 隨機洗牌演算法（Fisher-Yates Shuffle）

在使用者點擊「開始探索」時調用，徹底打破分類順序，避免作答防禦心理：

```
function shuffleQuestions(arr) {
  const shuffled = [...arr];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

```

## 5. 計分模型與象限映射演算法（Scoring & Mapping）

### 5.1 計分方式

* 每一題採用李克特 5 點選擇（1 分：非常不符合 ～ 5 分：這完全就是我！）。

* 使用者作答儲存於 Map 或 Object：`{ [questionId]: score }`。

* 總分計算：

  * **情緒指數** $E$ = $Q1 + Q2$（分值 2～10）

  * **事務指數** $T$ = $Q3 + Q4$（分值 2～10）

  * **培育指數** $N$ = $Q5 + Q6$（分值 2～10）

  * **督促指數** $C$ = $Q7 + Q8$（分值 2～10）

### 5.2 風格歸類邏輯

* **焦點判斷**：$E \ge T$ $\rightarrow$ 偏向情緒；反之 $\rightarrow$ 偏向事務。

* **姿態判斷**：$N \ge C$ $\rightarrow$ 偏向培育；反之 $\rightarrow$ 偏向督促。

| 關係姿態 \\ 焦點取向 | 關注情緒 ($E \ge T$) | 關注事務 ($T > E$) | 
 | ----- | ----- | ----- | 
| **培育型 (**$N \ge C$**)** | **陪伴聆聽者**（心理安全感容器） | **探索聆聽者**（澄澈的反射鏡） | 
| **督促型 (**$C > N$**)** | **覺察聆聽者**（情緒肌肉教練） | **行動聆聽者**（堅實行動後盾） | 

### 5.3 象限座標映射（Coordinate Calculation）

用以在前端渲染動態指示點（Pin）：

* **X 軸（水平：培育** $\leftrightarrow$ **督促）**：
  

  $$
  \Delta X = C - N \quad (\text{範圍 } -8 \sim +8)
  $$

  $$
  \text{Position X (\%)} = 50 + \left( \frac{\Delta X}{8} \right) \times 32\%
  $$

  
  （限制在 $18\% \sim 82\%$ 範圍內避免觸壁）

* **Y 軸（垂直：事務** $\leftrightarrow$ **情緒）**：
  

  $$
  \Delta Y = T - E \quad (\text{範圍 } -8 \sim +8，E \text{ 越大越往上})
  $$

  $$
  \text{Position Y (\%)} = 50 + \left( \frac{\Delta Y}{8} \right) \times 32\%
  $$

  
  （限制在 $18\% \sim 82\%$ 範圍內避免觸壁）

## 6. 頁面模組切換流程（State Machine）

頁面由單一容器承載，透過隱藏/顯示（CSS `hidden` 與 `fade-in` 動畫）無刷新切換：

1. `#panel-welcome`（首頁／引導區）：

   * 呈現 Listenfy 雙子向量 Logo。

   * 測驗主標題：「遇見你的傾聽超能力：日常陪伴取向風格探索」。

   * 探索指引彈窗（Modal）：闡明焦點取向與關係姿態的探索初衷。

2. `#panel-quiz`（作答區）：

   * 當前題號與流暢進度條（`width: (index + 1) / 8 * 100%`）。

   * 題目文字區塊（排版留白，避免外框過度壓迫）。

   * 5 點直覺選項列表（每題點選後即平滑自動推進至下一題，提供「回上一題修改」功能）。

3. `#panel-loading`（過渡動畫）：

   * 700ms 溫和的調頻過渡（「正在梳理你的傾聽羅盤...」）。

4. `#panel-result`（探索報告）：

   * 象限落點座標圖（帶有平滑位移動畫）。

   * 測驗結果風格卡（包含超能力描述、羅盤解讀）。

   * 功能按鈕列：使用 `html2canvas` 產生圖卡、剪貼簿文字一鍵複製。

   * 文末引導：「寫在旅程開始之前」＋ 連接外部 Google 表單（學員填報通報）。

## 7. 後續擴展建議

* **Google Form 預先填入（Pre-filled URL）**：
  可將計算結果（例如風格代碼 `A`、座標點 `E8_T4_N7_C5`）透過網址參數（Query Params）帶入 Google 表單的輸入欄位，免去學員二次手動輸入的困擾。

* **無後端事件追蹤（Optional）**：
  若需統計大眾作答落點分布，可無縫串接 Google Analytics 4 (GA4) 的自訂事件，或發送至 Google Apps Script (GAS) 試算表收集去識別化資料。