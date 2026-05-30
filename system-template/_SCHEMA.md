# [SYSTEM-NAME] Frontmatter Schema 規範

> **版本**：v1.0  
> **日期**：YYYY-MM-DD  
> **用途**：定義 `raw/` 下所有條目的 YAML Frontmatter 格式

---

## 必填欄位

| 欄位 | 類型 | 說明 |
|------|------|------|
| `id` | `string` | 唯一標識符（小寫、中線連接） |
| `category` | `string` | 分類代碼 |
| `title` | `string` | 標題 |
| `key_concepts` | `list` | 核心概念列表（用於查詢匹配） |
| `key_figures` | `list` | 關鍵人物列表，每個元素含 `name`, `lifespan`, `role` |
| `sources` | `list` | 文獻來源（建議 APA 第 7 版） |

## 可選欄位

| 欄位 | 類型 | 說明 |
|------|------|------|
| `title_en` | `string` | 英文標題 |
| `period` | `string` | 時間範圍 |
| `discipline` | `string` | 學科領域 |
| `search_queries` | `list` | 搜索關鍵詞 |

## 命名規範

```
raw/{YYYYMMDD}-{short-id}.md
```

- `YYYYMMDD` = 關鍵歷史錨點日期
- `short-id` = 小寫 kebab-case 標識符
