# MECW-index 任務日誌

> **最後更新**：2026-05-30  
> **狀態**：Phase 1 ✅ Phase 2 ✅（基礎索引完成）

---

## 2026-05-30 — 第二院正式建立

**執行者**：Copilot (DeepSeek V4 Pro)

### Phase 0：源數據獲取
- Clone MARX-ZH-CN/wikirouge-MECW-2026-Jan-ver（CC0，230MB）
- 50 卷 MECW，6,760 HTML + 3,143 archive HTML

### Phase 1：HTML→MD 全量轉換
- 撰寫 `scripts/convert-mecw-html-to-md.py`（~200 行）
- 成功轉換全部 50 卷，6,759 篇 Markdown（77MB）
- 類型分佈：4,306 letters / 2,211 articles / 162 chapters / 80 paratexts
- 年跨度：1818–2004，核心 1835–1895 佔 94.2%

### Phase 2：基礎設施
- 複製 `system-template/` 從 ECC（方法論共享）
- 建立 `scripts/build-compiled-db.py`：6,706 文獻 → `compiled-documents.json` (3.6 MB)
- 建立 `AGENTS.md` v0.1：兩院制協作協議
- 建立 `SCHEMA.md` v0.1：MECW 專用 Frontmatter 規範
- 建立 `GRANDPLAN.md` v0.1：階段藍圖
- Git 初始化 + push 至 https://github.com/Octy-devp/MECW-index

### 關鍵數據

| 指標 | 數值 |
|------|:---:|
| 源數據 | 230MB HTML |
| 轉換後 | 77MB Markdown |
| 編譯資料庫 | 3.6 MB JSON |
| 轉換腳本 | ~200 行 Python |
| 基礎設施建立 | ~2 小時 |

---

## 待辦

| 項目 | 狀態 |
|------|:---:|
| 人物索引（通信對象網絡） | ⬜ |
| 地點索引（London/Paris/Brussels...） | ⬜ |
| DCA 試點（5 篇關鍵文獻） | ⬜ |
| CROSS-CHAMBER.md（與 ECC 交叉張力） | ⬜ |
| 頻譜分析（theoretical_tension） | ⬜ |
