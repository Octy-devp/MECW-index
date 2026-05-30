# ECC 系統索引模板 v1.0

> **用途**：快速建立一個與 ECC 場景/知識體系架構一致的索引系統。
> **設計原則**：Frontmatter SSOT、雙軌 Prefix、編譯查詢、獨立日誌。

---

## 使用方式

```bash
# 1. 複製模板
cp -r system-template/ my-new-system/

# 2. 自訂 _SCHEMA.md（定義你的 Frontmatter 欄位）
# 3. 在 raw/ 目錄中建立 .md 條目
# 4. 執行編譯
python scripts/_build-compiled-db.py
python scripts/_build-prefix.py

# 5. 查詢
python scripts/_query.py stats
```

---

## 目錄結構

```
my-new-system/
├── _SCHEMA.md              # Frontmatter 規範（SSOT）
├── _TASKLOG.md             # 任務日誌
├── _INDEX.md               # 覆蓋進度看板
├── _AGENT-SKILL.md         # Agent 操作技能文檔
│
├── scripts/
│   ├── _build-compiled-db.py   # 將 raw/*.md 編譯為 compiled-{name}.json
│   ├── _build-prefix.py        # 生成 AI Prefix 文本
│   ├── _validate-schema.py     # Frontmatter 格式校驗
│   └── _query.py               # CLI 查詢工具（search/list/stats/gap）
│
├── raw/
│   └── _EXAMPLE.md             # 範例條目
│
└── data/
    ├── compiled-{name}.json    # 編譯庫（腳本自動生成）
    └── {name}-prefix.txt       # AI Prefix（腳本自動生成）
```

---

## 架構圖

```
                    ┌──────────────────────┐
                    │   AGENTS.md（可選）   │
                    │   任務路由表          │
                    └──────┬───────────────┘
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
   ┌───────────────┐               ┌───────────────┐
   │  系統 A        │               │  系統 B        │
   ├───────────────┤               ├───────────────┤
   │ _TASKLOG.md   │               │ _TASKLOG.md   │
   │ compiled-A    │               │ compiled-B    │
   │ .json         │               │ .json         │
   │ build-A-      │               │ build-B-      │
   │ prefix.py     │               │ prefix.py     │
   │ _AGENT-       │               │ _AGENT-       │
   │ SKILL.md      │               │ SKILL.md      │
   └───────────────┘               └───────────────┘
```

## 核心設計模式

### 1. Frontmatter SSOT
所有中繼資料存在 YAML Frontmatter 中，不建立中央資料庫。驗證腳本僅檢查 Frontmatter 格式，不修改原始條目。

### 2. 編譯層 → 濃縮

`_build-compiled-db.py` 將所有 `raw/*.md` 提取為單一 JSON。

```
raw/001.md + raw/002.md + ... + raw/136.md
        │
        ▼  _build-compiled-db.py
        │
compiled-knowledge.json  （一個檔案，所有條目的 Frontmatter + 摘要）
```

**為什麼要編譯？** 如果每次查詢都讓 Agent 逐一 `grep` → `read_file` 一百多個檔案，Token 成本巨大。編譯成單一 JSON 後，Prefix 和 Query 腳本都讀它，不再需要遍歷原始目錄。

### 3. Prefix 層 → AI 的被動記憶

`_build-prefix.py` 從 compiled JSON 生成濃縮索引文本（~9K tokens）。

```
compiled-knowledge.json
        │
        ▼  _build-prefix.py
        │
prefix.txt  （約 9,000 tokens 的目錄式摘要）
```

| 特性 | 說明 |
|------|------|
| **誰用** | AI Agent |
| **何時** | 啟動時載入 System Prompt |
| **機制** | **被動**——Agent 不需要問，開局就知道全庫有什麼 |
| **內容** | 分類目錄 + 每條一行摘要 + 關鍵詞索引 |
| **比喻** | 圖書館的「館藏總目錄」——翻一頁就知道有哪些書 |

> ⚠️ Prefix **不是查詢工具**。它是給 Agent 建立「全局認知」用的——讓 Agent 在回答問題前已經知道該去哪裡找答案。

### 4. 查詢層 → Agent 的主動工具

`_query.py` 提供 CLI，Agent 在**需要具體內容時**調用。

```
$ python scripts/_query.py search "NSPV"
$ python scripts/_query.py concept "clearing"
$ python scripts/_query.py list --cat 340
$ python scripts/_query.py stats
$ python scripts/_query.py gap
```

| 特性 | 說明 |
|------|------|
| **誰用** | Agent（或人類開發者） |
| **何時** | 執行任務期間，需要精確定位時 |
| **機制** | **主動**——Agent 調用 CLI 命令，返回 JSON/text 結果 |
| **內容** | 針對性查詢結果（匹配的條目 ID、摘要、相關概念） |
| **比喻** | 圖書館的「檢索終端」——輸入關鍵字，找到具體書架位置 |

> ⚠️ 查詢層 **不載入 AI context**。它是一個外部工具，Agent 調用它就像調用 `grep` 或 `read_file`——只消耗調用命令的少量 Token，不消耗結果內容的 Token（除非 Agent 決定讀取結果）。

### 5. 獨立日誌
每個系統有獨立的 `_TASKLOG.md`，不與其他系統的日誌混雜。主專案的 AGENTS.md 提供路由表決定 Agent 讀取哪個日誌。

### 6. 為什麼這樣設計？—— 80% 搜尋成本削減

這是整個架構的核心價值。沒有這套系統時，Agent 的工作流程是：

```
┌─────────────────────────────────────────────────────┐
│  ❌ 無系統索引時                                      │
│                                                     │
│  問題：「NSPV 的史實原型是什麼？」                      │
│                                                     │
│  Agent 動作：                                        │
│  1. grep "NSPV" 所有 raw/*.md       → 找到 25 個檔案  │
│  2. read_file 25 次（每次 50-200 行）                 │
│  3. 發現 20 個只是順便提及，只有 5 個真正相關           │
│  4. 重讀那 5 個檔案的完整內容                          │
│                                                     │
│  總 Token 成本：約 15,000-25,000 tokens               │
│  有效資訊比例：~20%（其餘 80% 是誤報和不相關內容）      │
└─────────────────────────────────────────────────────┘
```

有了這套系統後：

```
┌─────────────────────────────────────────────────────┐
│  ✅ 有編譯 + Prefix + Query 時                        │
│                                                     │
│  問題：「NSPV 的史實原型是什麼？」                      │
│                                                     │
│  Agent 動作：                                        │
│  1. Prefix 已在 context（9K tokens）→ 知道有哪些條目   │
│  2. _query.py search "NSPV"         → 直接返回 5 條   │
│  3. 選擇性 read_file 1-2 個最相關的 raw 檔案           │
│                                                     │
│  總 Token 成本：約 3,000-5,000 tokens                 │
│  有效資訊比例：~90%（幾乎全是相關內容）                 │
│                                                     │
│  削減幅度：~80%                                       │
└─────────────────────────────────────────────────────┘
```

**核心原理**：

| 無系統 | 有系統 | 節省 |
|--------|--------|------|
| Agent 盲目 grep → 大量誤報 | Prefix 已載入 → Agent 知道去哪裡找 | ~40% |
| read_file 遍歷不相關檔案 | Query CLI 精確返回匹配條目 | ~30% |
| 重複讀取同一檔案驗證 | compiled JSON 單一數據源 | ~10% |
| **合計** | | **~80%** |

> 簡而言之：**讓機器做機器擅長的事（索引、搜尋、比對），讓 AI 做 AI 擅長的事（理解、推理、創作）。** Prefix 和 Query 的任務就是把「找資料」的 Token 成本壓到最低，讓 AI 的 80% 算力用於真正需要思考的工作。

---

## Schema 設計要點

每條 `_EXAMPLE.md` 的 Frontmatter 至少包含：

| 欄位 | 類型 | 說明 |
|------|------|------|
| `id` | `string` | 唯一標識符 |
| `category` | `string` | 分類代碼 |
| `title` | `string` | 標題 |
| `key_concepts` | `list` | 核心概念（用於查詢匹配） |
| `key_figures` | `list` | 關鍵人物 |

可選：自訂分析結構（如 DCA 的四段式 `crisis/lag/alternative/direction`）。

---

## 腳本自訂指南

每個 `_*.py` 腳本中包含 `## CUSTOMIZE HERE` 標記，指示需要修改的部分：

1. `_build-compiled-db.py`：修改路徑、Frontmatter 欄位映射
2. `_build-prefix.py`：修改系統提示詞、分類名稱對照表
3. `_validate-schema.py`：修改必填欄位清單
4. `_query.py`：修改分類對照表
