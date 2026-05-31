# MECW-index — 馬克思恩格斯全集結構化索引系統

> 基於 T-SALC 三層認知架構（二進制驗證 / 三進制語義 / 頻譜制節律）  
> DCA（危機-滯後-替代-方向）方法論的 Marx/Engels 校準基準  
> `git clone → bash setup.sh → 即用`

---

## 快速開始

```bash
git clone https://github.com/Octy-devp/MECW-index.git
cd MECW-index
bash setup.sh
```

## 系統架構

```
MECW-index/
├── index/
│   ├── documents-raw/     ← 6,759 篇 Markdown（MECW 50 卷）
│   ├── characters/        ← 50 位通信對象檔案
│   ├── data/
│   │   ├── compiled-documents.json      ← 6,706 文獻編譯
│   │   ├── character-network.json       ← 694 人通信網絡
│   │   ├── keyword-timeseries.json      ← 8 詞 × 60 年
│   │   ├── theoretical-spectrum.json    ← 理論張力頻譜 v0.3
│   │   ├── dca-structure-timeseries.json← DCA 結構時間序列
│   │   └── mecw-prefix.txt             ← AI Prefix v2 (CoT)
│   └── data/prefix-emitted/            ← 多平台格式（Claude/DeepSeek/GPT）
├── scripts/
│   ├── build-compiled-db.py            ← 編譯器
│   ├── build-mecw-prefix.py            ← Prefix 生成
│   ├── build-theoretical-spectrum.py   ← 頻譜計算
│   ├── build-dca-timeseries.py         ← DCA 結構時間序列
│   ├── extract-character-network.py    ← 人物網絡
│   ├── bulk-analyze.py                 ← 關鍵詞 + 十年摘要
│   ├── mecw-query-ai.py               ← DeepSeek API 查詢
│   ├── emit-prefix.py                  ← 格式發射器
│   └── validate-mecw.py               ← 驗證器
├── .taskbook/
│   ├── dca-calibration-20.md           ← DCA 校準清單
│   ├── dca-results/                    ← API DCA 提取結果
│   └── reports/                        ← 分析報告
├── AGENTS.md                           ← 協作協議
├── SCHEMA.md                           ← Frontmatter 規範
├── GRANDPLAN.md                        ← 藍圖
└── TASKLOG.md                          ← 進度日誌
```

## 核心數據

| 指標 | 數值 |
|------|:---:|
| 文獻總數 | 6,759 |
| MECW 卷數 | 50 |
| 年跨度 | 1818–2004 |
| 核心時期 (1835–1895) | 6,367 篇 (94.2%) |
| 類型分佈 | 4,306 封信 / 2,211 篇文章 / 162 章節 |
| 通信對象 | 694 人（Marx↔Engels: 1,545 封） |
| DCA 校準基準 | 20/20 完成 |
| 頻譜版本 | v0.3 (ANOVA 校準) |

## T-SALC 三層

| 層級 | 名稱 | MECW 實現 | 狀態 |
|:---:|------|---------|:---:|
| L1 | 二進制（機械層） | compiled-db + 驗證 + 查詢 | ✅ |
| L2 | 三進制（語義層） | DCA 20/20 + Prefix v2 CoT + API | ✅ |
| L3 | 頻譜（節律層） | 理論張力 Butterworth + DCA 結構交叉譜 | ✅ v0.3 |

## 可用命令

```bash
# 查詢
python3 scripts/query.py --stats              # 全庫統計
python3 scripts/query.py --timeline           # 60年年表
python3 scripts/query.py --contact "Ferdinand Lassalle"  # 通信記錄

# AI 分析（需 DEEPSEEK_API_KEY）
python3 scripts/mecw-query-ai.py --dca MECW35-004         # 單篇DCA提取
python3 scripts/mecw-query-ai.py --dca-batch P1           # 批量提取
python3 scripts/mecw-query-ai.py "Paris Commune" --api    # 自然語言+AI

# 頻譜
python3 scripts/build-theoretical-spectrum.py  # 重建理論張力頻譜

# 驗證
python3 scripts/validate-mecw.py              # 全庫校驗
```

---

## ⚠️ 已知局限（Known Limitations）

> 2026-05-31，基於 134 篇 DCA 抽樣 + 殘差考古學首次分析

### 一、長波 ≠ 物質歷史週期

`theoretical_longwave` 是從 MECW 文本的**關鍵詞頻率**經 Butterworth 低通濾波計算得出。它反映的是「Marx/Engels 的寫作注意力長期趨勢」，而非獨立的宏觀經濟週期（Kondratiev waves）。兩者可能相關，但尚未與外部經濟史數據做交叉驗證。

- **症狀**：`state` 關鍵詞權重過高（3.78），1843 年萊茵報查封事件造成尖峰，Butterworth 平滑後迫使 1848 年革命處於數學上的「下行段」
- **影響**：長波/中波/短波三層分解的物理意義需要謹慎對待——它們是「關鍵詞注意力的頻率成分」，不是「資本主義的結構節律」
- **待修復**：與 NBER 經濟週期數據、Kondratiev 價格指數做交叉驗證；考慮以主題建模（topic modeling）取代關鍵詞加權

### 二、Crisis Type 映射表是預設的

`LONGWAVE_CRISIS_EXPECTATION` 映射表（長波相位 → 預期危機類型）是根據歷史常識手寫的，不是從數據中學習的。94/134（70%）的 DCA 結果被標為「理論突變體」，部分原因正是映射表覆蓋範圍有限——Marx/Engels 的 crisis type 詞彙遠比手寫表豐富。

- **影響**：「對齊」標籤只能解讀為「crisis type 恰好落在映射表的範圍內」，不能解讀為「歷史的客觀共振」
- **待修復**：從 DCA 數據中無監督聚類 crisis type，再與頻譜相位做統計檢驗（而非規則匹配）

### 三、Few-Shot Prefix 可能造成回音室

系統提示詞（Version B prefix）以《共產黨宣言》第一章（1848）為 DCA 示範。這可能導致 AI 在處理 1848 年前後文獻時，輸出的 crisis type 向示範文本靠攏。

- **待驗證**：A/B/C 三版 prefix 對照實驗（示範文本分別為 1848 / 1867 / 1875），檢測 crisis type 分佈是否顯著偏移

### 四、抽樣策略與未覆蓋文獻

當前 DCA 基於分層抽樣（134/2,259 篇 article+chapter，覆蓋率 6%）。4,304 封書信完全未做 DCA 提取——它們可能包含不同類型的 crisis diagnosis（更即時、更組織化、更個人化）。

---

## 🧪 未來研究遊樂場（Future Research Playground）

以下六個方向是 DCA + 頻譜 + 人物網絡的組合玩法。每一個都可以獨立發展成論文或工具。

---

### 一、概念流行病學（Concept Epidemiology）

把 `character-network.json`（人際網絡）疊上 DCA 提取結果，變成**概念傳染網絡**。

- **節點**：人物（Marx、Engels、Lassalle、Bebel…）
- **邊**：兩人通信中共享的 crisis type 或 lag mechanism
- **權重**：DCA 結構相似度

**核心玩法**：追蹤一個 DCA 元素的「零號病人」。`revolutionary dictatorship of the proletariat` 第一次出現在誰的文本？透過什麼 lag mechanism（organizational？ideological？）被傳染給下一位？在頻譜上對應長波的哪個相位？

**假說**：有些概念在長波 crest 時被「發明」，在中波 trough 時被「誤傳」，在短波 spike 時被「背叛」——比傳統觀念史多了**物質節奏的維度**。

---

### 二、殘差考古學（Residual Archaeology）🔄 已初步驗證

頻譜把信號切成長波（正規化）+ 中波（週期）+ **短波（殘差）**。傳統做法把短波當 noise。反過來：**專門獵殺短波中的異常**。

**玩法**：
1. 找出 `theoretical_shortwave` 絕對值最高的 20 個年份 ✅
2. 提取這些年份所有文本的 DCA，追問：這些 crisis type 是否無法被當時的長波趨勢解釋？ ✅
3. 標記為 **「理論突變體」（theoretical mutants）** ✅

**首次分析結果**（2026-05-31，134 篇 DCA）：
- 94 篇被標記為理論突變體（70%），22 篇對齊
- **1875 年**（短波 +3.21）是最大異常：《哥達綱領批判》的 crisis type 為 `organizational_degeneration`——物質條件允許前進（長波上升），政治組織卻在後退
- 完整報告：`.taskbook/reports/residual-archaeology-20260531.md`
- 已知局限：見上方 ⚠️ 節

**案例**：1857 年（經濟危機）短波異常高，但 DCA 顯示 Marx 在寫的卻是 *theoretical retreat* 類型（《政治經濟學批判》導言中對方法論的退縮式反思）——物質危機高峰時，理論反而在後撤。這種張力本身就是最有價值的歷史問題。

---

### 三、多聲部 DCA 合唱（Polyphonic DCA）

讓系統**故意精神分裂**。同一篇文本，用三種理論人格分別提取 DCA：

| 人格 | 預設 |
|------|------|
| **正統派** | 強調 productive forces → class struggle → revolution 的線性邏輯 |
| **阿爾都塞派** | 尋找 epistemological break，lag 一定是 theoretical |
| **自治主義派** | crisis 一定是 class composition 的變化，alternative 從工人自主出發 |

**玩法**：
- 比較三種人格對同一文本的 DCA 提取差異
- 結構化差異本身：哪些欄位永遠一致（direction_constraint 中的 material limits），哪些永遠分裂（lag_mechanism 的層數歸因）
- 用頻譜分析**分歧的時間分佈**：某些年份所有流派同意 crisis 是 organizational，但對 lag 大打出手？

產出：一張 **「詮釋學爭議地形圖」**，比任何文獻綜述更精確地標示馬克思主義傳統中的不可通約點。

---

### 四、預測性合成（Predictive Synthesis）

用頻譜外推 + DCA 模式匹配，做**反事實生成**。

**步驟**：
1. 選一個 Marx 死後的事件（1905 年俄國革命、1929 年大蕭條、2026 年 AI 勞動替代）
2. 在頻譜上找到歷史上最接近的 longwave + midwave 相位組合
3. 提取該相位附近所有文本的 DCA 結構，建立「危機反應模式庫」
4. 以此為 few-shot prompt，要求 AI 生成：「如果 Marx/Engels 在 1905 年寫一篇關於彼得堡總罷工的文本，其 DCA 結構會是什麼？」

**關鍵限制**：輸出必須標記為 `synthetic / counterfactual`，且必須顯示基於哪個歷史相位的外推。這不是「預言」，而是**結構類比的顯影**。

---

### 五、理論地形圖（Topographic Map）

跳出時間軸。把每篇文獻的 DCA 當成向量：

```
[crisis_type_onehot, lag_layers_count, alternative_elements_count, direction_material_constraint_strength]
```

用 UMAP / t-SNE 降維，把 6,706 篇文獻攤平成一張二維地圖。

**玩法**：
- 地形高度 = `tension_per_doc`（頻譜張力值）
- 顏色 = decade
- 你會看到「山脈」和「峽谷」：某些區域密集聚集高張力革命文本，某些是低張力書信平原
- 點擊任意一點，彈出 DCA 詳情和原文摘錄

這比時間軸更直觀：**Marx 的思想空間不是線性進步，而是有引力井和排斥區的複雜地形**。

---

### 六、聲音化（Sonification）

把頻譜的三條波直接轉成聲音：

| 波 | 聲音 | 意義 |
|----|------|------|
| **長波** | 極低頻 drone（20–40 Hz） | 歷史的底層結構 |
| **中波** | 中頻節奏脈衝（2–4 Hz） | 十年週期的「心跳」 |
| **短波** | 高頻 glitch / noise | 突發事件和異常 |

**玩法**：讓用戶「聽見」1835–1895 年的理論張力。1871 年（巴黎公社）中波突然加速；1875 年（哥達）短波產生尖銳 artifact。這不是藝術裝置，而是**認知輔助**——人耳對時間序列異常比眼睛更敏感。

---

## 許可

源數據：MARX-ZH-CN/wikirouge-MECW-2026-Jan-ver (CC0 Public Domain)  
索引系統：MIT License

## 引用

```
@misc{mecw-index-2026,
  title = {MECW-index: A Structured Index of Marx/Engels Collected Works},
  author = {Octy-devp},
  year = {2026},
  url = {https://github.com/Octy-devp/MECW-index}
}
```
