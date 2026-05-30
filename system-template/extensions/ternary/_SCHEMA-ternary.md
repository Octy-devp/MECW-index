# 三進制審計模組 — Schema 擴展字段定義

> **版本**：v1.0  
> **日期**：2026-05-29  
> **依賴**：主系統的 `_SCHEMA.md`（Layer 1）  
> **用途**：定義三進制審計所需的 Frontmatter 可選字段。將此文件的字段定義**合併**到主 `_SCHEMA.md` 中（全部為 `required: false`）。  
> **設計文檔**：`docs/recommendations/recommendation-tsalc-spectrum-architecture.md` § 二

---

## 設計理念（為什麼需要這些字段）

### 問題：二進制 Schema 的盲區

傳統的 Schema 驗證只能檢查「格式對不對」——YAML 語法、必填欄位、日期格式。它無法檢查「內容是否誠實」。

```
二進制 Schema 能回答的：
  ✅ date 格式是 YYYY-MM-DD 嗎？
  ✅ sources 列表不為空嗎？
  ✅ key_figures 包含 name + lifespan 嗎？

二進制 Schema 不能回答的：
  ❌ 這個 mood 標籤真的有文本證據支持嗎？
  ❌ 文本中是否存在支持相反 mood 的同等強度證據？
  ❌ 這個條目的歷史判斷是否有學術爭議？
```

### 解決：三元認知單元

三進制 Schema 擴展不取代二進制驗證——它在二進制之上**疊加**一個新維度：**確定性狀態**。

每個原本的「內容字段」（如 `mood`、`analysis`、`conclusion`）可以被包裝為一個**三元認知單元**：

```yaml
# 舊（二進制）：只說「是什麼」，不說「有多確定」
mood: "疏離"

# 新（三進制）：同時說「是什麼」「有多確定」「有什麼反證」
mood:
  primary: "疏離"
  status: contested       # ← 這是二進制 Schema 無法表達的維度
  dissent:
    - position: "溫情/依戀"
      evidence: [scene-128, scene-203]
```

### 關鍵設計決策：全部字段為 `required: false`

這是整個可組裝式架構的核心。如果三進制字段是必填的，那麼：
- 所有舊條目必須回填 → 破壞向下相容
- 移除 ternary 模組後，Schema 驗證會報錯 → 破壞可拆卸性

因此**所有三進制字段都是可選的**。這意味著：
- 舊條目完全不需要修改
- 新條目可以選擇性使用三進制字段
- 移除 ternary 擴展後，驗證腳本不會報錯（只檢查必填字段）

---

## 通用三元認知單元

以下定義了一個**可復用的三元認知單元結構**，可套用到任何需要「不確定性標記」的字段：

```yaml
# === 三元認知單元（通用模板） ===
# 將任何原本是純值的字段升級為此結構
# 適用於：mood, analysis, conclusion, evaluation, classification... 任何需要標記確定性的字段

<field_name>:
  primary: <原始值>         # 主要判斷（對應舊 Schema 的純值）
  valence: <0.0~1.0>       # 強度／置信度
  status: <狀態>            # asserted | contested | unknown（三態的嚴格定義見下方）
  
  # 以下字段僅在 status: asserted 或 contested 時使用
  anchors:                  # 原始文本／數據錨定（證明這個判斷不是憑空而來）
    - source: <來源標識>     # 如 scene_id, line_number, document_id
      quote: <引用原文>      # 支持這個判斷的具體文本
      support: <0.0~1.0>   # 這段文本支持 primary 判斷的程度

  # 以下字段僅在 status: contested 時使用
  dissent:                  # 內部矛盾顯性化（這是三進制最有價值的字段）
    - position: <反方立場>   # 與 primary 矛盾的替代判斷
      evidence: [<來源列表>] # 支持反方的文本
      strength: <0.0~1.0>  # 反方證據的強度

  # 以下字段永遠是 null（基層節點被禁止輸出綜合判斷）
  synthesis: null           # 敘事閹割——防止基層節點用「成長」「辯證統一」等敘事填補證據空白
```

### 三態的嚴格定義

| 狀態 | 定義 | 觸發條件 | 範例 |
|------|------|---------|------|
| **asserted** | 有直接文本證據支持的判斷，無同等強度反證 | anchors ≥ 3, 所有 support ≥ 0.7, dissent 為空或 strength < 0.3 | 「scene-47 的對白明確顯示憤怒」 |
| **contested** | 文本中存在支持判斷和支持反方的**同等強度**證據 | 正反證據強度差 < 0.3，或存在至少 1 個 dissent.strength ≥ 0.5 | 「scene-47 的對白可解讀為憤怒或恐懼，兩者都有文本支持」 |
| **unknown** | 文本信息不足以做出判斷 | anchors < 2，或所有 support < 0.5 | 「scene-47 缺乏對白，無法判斷情緒」 |

### 為什麼 contested ≠ 「不確定」

`contested` 不是「我不確定」。它是**「我確定文本中有矛盾」**——這是一個**正向認知狀態**，不是認知缺失。

`unknown` 才是「認知缺失」——文本信息不足。

這兩個狀態的區分是整個三進制架構最有價值的設計：**contested 告訴你「這裡有張力，需要人工判斷」；unknown 告訴你「這裡是盲區，需要更多數據」。**

---

## 具體字段定義

### `audit_v2` — 三進制審計記錄（場景／條目級）

```yaml
audit_v2:
  # === 審計狀態 ===
  status: asserted            # asserted | contested | unknown
                              # 這是整個審計的核心輸出——一個三態判斷
  
  # === 審計上下文 ===
  auditor: "v4-semantic-audit-v2.py"  # 哪個腳本／模型做的審計
  audited_at: "2026-05-29"            # 審計日期
  confidence: 0.87                    # 審計器對自身判斷的信心（非 primary 的 confidence）
  
  # === 頻譜上下文（僅當 spectrum 擴展啟用時存在） ===
  spectrum_context:                   # 審計時的頻譜坐標（來自 Layer 3）
    longwave_phase: 0.314             # 場景在長波週期中的位置（0→1）
    longwave_trend: "rising"          # 長波趨勢方向
    interference_pattern: "destructive"  # 頻譜干涉模式
    interference_note: "長波上升期出現短波高能量負向脈衝"
  
  # === 人工介入標記 ===
  human_override_required: true       # 是否需要人工審查
  human_override_note: "contested 場景——正反證據強度差 < 0.3，建議人工裁定"
  
  # === 證據摘要 ===
  evidence_summary:                   # 給人工審查者的快速摘要
    primary_evidence_count: 3
    dissent_evidence_count: 2
    key_tension: "scene-89 的認同 vs scene-203 的敵意無法調和"
```

### `mood` — 三元情緒標籤（場景級，升級現有欄位）

```yaml
# 將 SCHEMA.md 中現有的 mood 字段從純字串升級為：
mood:
  primary: "疏離"             # 主要情緒判斷（向後相容：舊的 mood: "疏離" → mood.primary: "疏離"）
  valence: 0.82               # 情緒強度（0=中性, 1=極強）
  status: contested           # asserted | contested | unknown
  anchors:
    - scene: 47
      line: 1284
      quote: "他退後一步，像是被燙傷"
      support: 0.91
    - scene: 128
      line: 8932
      quote: "他忽然笑了，伸手替她撥開頭髮"
      support: 0.23           # ← 支持度低，這是反證
  dissent:
    - position: "溫情/依戀"
      evidence: [scene-128, scene-203]
      strength: 0.74
  synthesis: null              # 基層強制留空
```

### `analysis` — 三元分析標籤（條目級，知識庫用）

```yaml
# 知識庫條目中對歷史事件的判斷，同樣可以使用三元結構
# 例如：一篇關於 1903 年 RSDLP 分裂的知識條目

analysis:
  primary: "1903 年分裂是組織形式爭論的產物，雙方均為革命馬克思主義者"
  valence: 0.78
  status: asserted
  anchors:
    - source: "lenin-1904-one-step-forward"
      quote: "..."
      support: 0.85
  dissent: []                  # 無反證 → asserted
  synthesis: null
  
  # 如果存在學術爭議：
  # status: contested
  # dissent:
  #   - position: "1903 年分裂本質上是革命 vs 改良的路線鬥爭"
  #     evidence: ["stalinist-historiography-1938"]
  #     strength: 0.65
```

---

## 合併到主 Schema 的方式

在你的 `_SCHEMA.md` 的「可選欄位」部分加入以下內容：

```yaml
# === 三進制審計字段（來自 extensions/ternary/，全部 optional） ===
audit_v2:
  type: dict
  required: false
  description: "三進制審計記錄。由 _audit-ternary.py 自動生成。"
  fields:
    status:
      type: string
      required: true  # 若 audit_v2 存在，status 必填
      allowed_values: ["asserted", "contested", "unknown"]
    auditor: { type: string, required: false }
    audited_at: { type: string, required: false }
    confidence: { type: float, required: false, min: 0, max: 1 }
    human_override_required: { type: boolean, required: false }

# mood 字段升級（向後相容——舊的純字串 mood 仍然合法）
mood:
  type: any  # string | dict
  required: false
  description: "情緒標籤。可以是純字串（舊格式）或三元結構（新格式）。"
```

---

## 向後相容性保證

| 舊格式 | 新格式 | 是否相容 |
|--------|--------|:------:|
| `mood: "疏離"` | `mood: {primary: "疏離", status: asserted}` | ✅ 舊格式仍合法，腳本自動檢測類型 |
| 無 `audit_v2` 字段 | 有 `audit_v2` 字段 | ✅ 全部 optional，舊條目不受影響 |
| 二進制驗證腳本 | 二進制 + 三進制 | ✅ 二進制腳本只檢查必填字段，忽略 optional 字段 |
