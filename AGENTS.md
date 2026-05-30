# MECW 馬克思主義文獻索引 — 協作協議

> **版本**：v0.1  
> **日期**：2026-05-30  
> **用途**：定義所有 AI 代理在操作 MECW-index（第二院）時必須遵守的規則  
> **核心原則**：Marx/Engels Collected Works (MECW) 50 卷的結構化索引系統。所有元數據以 YAML Frontmatter 為 SSOT。  
> **架構**：兩院制蘇維埃——與 ECC（第一院）平行自治，共享 system-template 方法論，不共享數據。

---

## 一、專案概覽

英文馬克思恩格斯全集（MECW）結構化索引，6,759 篇文獻，50 卷。源數據來自 MARX-ZH-CN/wikirouge-MECW-2026-Jan-ver（CC0）。

| 類型 | 數量 | 說明 |
|------|:---:|------|
| Letters | 4,306 | Marx/Engels 與數百通信對象的書信 |
| Articles | 2,211 | 新聞評論、理論文章、宣言 |
| Chapters | 162 | 《資本論》等著作章節 |
| Paratexts | 80 | 序言、後記、編輯註 |

| 時間 | 範圍 |
|------|------|
| 全跨度 | 1818–2004 |
| 核心時期 | 1835–1895（Marx/Engels 活躍期，94.2%） |

---

## 二、文件體系

| 優先級 | 檔案 | 用途 |
|--------|------|------|
| 1 | `GRANDPLAN.md` | 戰略藍圖（待建） |
| 2 | `SCHEMA.md` | Frontmatter 規範（待建） |
| 3 | `AGENTS.md` | **本文件** |
| 4 | `TASKLOG.md` | 進度與阻擋 |

### 源數據

| 目錄 | 說明 |
|------|------|
| `/workspaces/MECW-source/` | MECW 原始 HTML（只讀，不修改） |
| `index/documents-raw/` | HTML→MD 轉換後的文獻 |
| `index/data/compiled-documents.json` | 全庫編譯（3.6 MB） |

### 兩院制關係

| | ECC（第一院） | MECW-index（第二院） |
|------|:---:|:---:|
| 語料 | 架空歷史小說 | 馬克思主義理論文獻 |
| 文檔類型 | scene | document |
| 核心 Schema | scene_type, mood, characters | doc_type, author, theoretical_position |
| 頻譜信號 | valence (虛構情感) | theoretical_tension (理論張力) |
| DCA 對象 | 技術史危機 | 政治經濟學危機 |
| 交叉張力 | `CROSS-CHAMBER.md` | 協調委員會（待建） |

---

## 三、核心原則

| 原則 | 說明 |
|------|------|
| **SSOT** | Frontmatter 是文獻元數據的唯一真實來源 |
| **源數據只讀** | 禁止修改 `MECW-source/` 中的 HTML |
| **寧缺勿濫** | 若無法從 HTML 提取精確日期，保留原始字串，不發明 |
| **兩院平行** | MECW-index 有自己的 AGENTS/Schema/TASKLOG，不與 ECC 混淆 |
| **CC0 合規** | 所有產出遵循源數據的 CC0 許可 |

---

## 四、邊界

### 🚫 NEVER

| 操作 | 原因 |
|------|------|
| 修改 `MECW-source/` 下任何檔案 | 原始數據不可觸動 |
| 修改 ECC 的任何檔案 | 兩院平行自治 |
| 憑空發明日期、作者、理論立場 | 寧缺勿濫 |

### ✅ ALWAYS

| 操作 | 說明 |
|------|------|
| 結構變更後重建 `compiled-documents.json` | 確保索引同步 |

---

## 五、MECW 特有概念

### 文獻類型 (doc_type)

| 類型 | 說明 | 範例 |
|------|------|------|
| `letter` | 書信 | Marx to Engels, 1867-08-16 |
| `article` | 文章/評論 | The Eighteenth Brumaire |
| `chapter` | 著作章節 | Capital Vol.1 Ch.1 |
| `paratext` | 序言/後記/編輯註 | Preface to the First German Edition |
| `editorial` | 編輯委員會文本 | General Introduction |

### 理論張力 (theoretical_position) — 待實現

| 立場 | 說明 |
|------|------|
| `critique` | 對現有理論/制度的批判 |
| `defense` | 對自身立場的辯護 |
| `synthesis` | 新理論框架的建構 |
| `polemic` | 對特定對手的論戰 |
| `analysis` | 對具體局勢的實證分析 |

---

## 六、環境

| 約束 | 說明 |
|------|------|
| **Python** | 3.10+，優先 `/usr/bin/python3` |
| **依賴** | PyYAML（YAML 解析） |
| **語言** | 所有文檔使用繁體中文或英文 |
