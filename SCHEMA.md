# MECW 文獻 Frontmatter Schema

> **版本**：v0.1  
> **日期**：2026-05-30  
> **用途**：定義 MECW-index 所有 Markdown 文獻的 YAML frontmatter 規範  
> **適用範圍**：`index/documents-raw/volume-*/*.md`

---

## 一、必填欄位

| 欄位 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `id` | string | 唯一標識符，格式 `MECW{卷}-{編號}` | `MECW01-004` |
| `title` | string | 文獻標題 | `"Letter to Heinrich Marx, November 10, 1837"` |
| `volume` | integer | MECW 卷號 (1–50) | `1` |
| `doc_type` | enum | `letter` / `article` / `chapter` / `paratext` / `editorial` | `letter` |
| `status` | enum | `raw`（初始）/ `reviewed` / `annotated` | `raw` |

---

## 二、可選欄位

| 欄位 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `author` | string | 標準化作者名 | `Karl Marx` / `Friedrich Engels` / `Karl Marx & Friedrich Engels` |
| `written` | string | 寫作日期（原始字串） | `"10 November 1837"` |
| `year` | integer | 年份（從 written 提取） | `1837` |
| `publication` | string | 首次出版資訊 | `"First Published: Die Neue Zeit No. 1, 1897..."` |
| `recipient` | string | 收信人（僅 letter） | `Heinrich Marx` |
| `source_language` | string | 原文語言 | `de` / `en` / `fr` |
| `translator` | string | 英譯者 | `Progress Publishers` |
| `theoretical_position` | enum | 理論立場（待實現） | `critique` / `defense` / `synthesis` / `polemic` / `analysis` |

---

## 三、日期格式

| 規則 | 說明 |
|------|------|
| 精確日期 | 從 HTML `Written` 欄位直接提取 |
| 模糊日期 | 保留原始字串，不發明（如 `"August 1871"`） |
| 年份提取 | `year` 欄位為整數，從 `written` 自動提取四位年份 |
| 無日期文獻 | `written: null`, `year: null`（如編輯前言） |

---

## 四、作者標準化

| HTML 原始值 | 標準化後 |
|------------|---------|
| `Karl Marx` | `Karl Marx` |
| `Friedrich Engels` | `Friedrich Engels` |
| `Karl Marx and Friedrich Engels` | `Karl Marx & Friedrich Engels` |
| `Progress Publishers` | 保留原值（編輯文本） |

---

## 五、與 ECC Schema 的對應

| MECW 欄位 | ECC 對應 | 差異 |
|-----------|---------|------|
| `id` | `id` | MECW 格式：`MECW{卷}-{編號}` |
| `doc_type` | `scene_type` | 理論文獻類型 vs 敘事場景類型 |
| `volume` | `arc` | 卷號 vs 篇章 |
| `status` | `status` | 相同 |
| `year` | `date` (year part) | 年份 vs 完整日期 |
| `theoretical_position` | `mood` | 理論立場 vs 情緒標籤 |

---

## 六、驗證規則

| 規則 | 檢查方式 |
|------|---------|
| `id` 唯一 | `build-compiled-db.py` 自動檢查 |
| `doc_type` 合法 | 僅接受五種枚舉值 |
| `year` 合理 | 1818–2004（超出範圍需人工確認） |
| `volume` 合理 | 1–50 |
