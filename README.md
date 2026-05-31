# MECW-index — 兩院制蘇維埃第二院

> 馬克思恩格斯全集（MECW）結構化索引系統  
> 基於 T-SALC 三層認知架構（二進制 / 三進制 / 頻譜制）  
> 兩院制蘇維埃架構——與 [ECC](https://github.com/Octy-devp/ECC)（第一院，架空小說索引）平行自治

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

## 兩院制關係

| | ECC（第一院） | MECW-index（第二院） |
|------|:---:|:---:|
| 語料 | 架空歷史小說 | 馬克思主義理論文獻 |
| 核心方法 | mood 標註 | DCA 提取 |
| 頻譜信號 | valence (虛構情感) | theoretical_tension (理論張力) |
| DCA 角色 | 應用對象 | 校準源 |
| 交叉 | `CROSS-CHAMBER.md` (待建) | |

---

## 未來發展方向

### 動態網絡層（Phase 8）

- **概念傳染網**：追蹤 "dictatorship of the proletariat" 從 1848→1875→1891 的 DCA 結構變形
- **問題迴路**：德國社會民主黨的理論退縮——1848 到 1890 年代，一條 40 年的滯後機制鏈
- **沉默地圖**：哪些文獻 DCA 欄位為 null？標示出框架的邊界與盲點

### 反向生成層（Phase 9）

- **歷史類比模擬器**：輸入當代事件 → 檢索最相似 historical crisis pattern → 合成馬克思式 DCA 分析
- **缺失文本重建**：基於已知 DCA 結構 + 馬克思慣用論證模式 → 生成可能性區間
- **教學對話系統**：學生上傳新聞 → 自動比對 MECW 中最接近的 DCA 案例

### 前端層（Phase 10）

- **Web 界面**：git clone → `bash setup.sh` → 本地瀏覽器即可使用
- **API 服務**：REST API 包裝 query + DCA 提取
- **可視化**：D3.js 交互式頻譜圖 + 人物網絡力導向圖

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
