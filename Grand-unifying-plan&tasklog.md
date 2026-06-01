# 兩院制蘇維埃 — 統合計劃與進度追蹤

> **版本**：v1.0  
> **日期**：2026-06-01  
> **用途**：跨專案（ECC + MECW-index + 未來 βₙ）的統一進度看板、共享方法論演進、聯合優先級決策  
> **同步**：本文件在 `/home/dev/projects/ECC/` 和 `/home/dev/projects/MECW-index/` 各有一份，手動保持同步  
> **同步協議**：修改時只改一邊（通常是 ECC 側），由 Copilot 負責同步到另一邊。禁止人類手動兩邊複製——避免版本漂移。  
> **上位約束**：兩院各自的 `GRANDPLAN.md` + `AGENTS.md`  
> **核心原則**：兩院平行自治，共享方法論基礎設施（system-template），不共享數據

---

## 一、兩院制全景

```
┌─────────────────────────────────────────────────────────────────┐
│                    兩院制蘇維埃認知系統                            │
│                                                                 │
│  ═══════════════════════════════════════════════════════════    │
│  共享方法論基礎設施（system-template/）                           │
│  ├── 二進制層：validate, check-line, global-resequence          │
│  ├── 三進制層：ternary extension（asserted/contested/unknown）   │
│  ├── 蘇維埃制：soviet extension（路由 + 張力圖譜）               │
│  └── 頻譜制：spectrum extension（Butterworth + mood-valence）    │
│  ═══════════════════════════════════════════════════════════    │
│                                                                 │
│  ┌─────────────────────────┐    ┌─────────────────────────┐     │
│  │  第一院：ECC             │    │  第二院：MECW-index       │     │
│  │  ─────────────────────  │    │  ─────────────────────   │     │
│  │  語料：架空歷史小說       │    │  語料：Marx/Engels 全集    │     │
│  │  文檔類型：scene         │    │  文檔類型：document        │     │
│  │  核心 Schema：mood,      │    │  核心 Schema：doc_type,   │     │
│  │    characters, locations │    │    author, theoretical_    │     │
│  │                          │    │    position               │     │
│  │  頻譜信號：valence (zg)   │    │  頻譜信號：theoretical_    │     │
│  │  外部基準：ha (CMH        │    │    tension (tt)           │     │
│  │    1900-1920 tension)    │    │  外部基準：ha_MECW (CMH    │     │
│  │                          │    │    1830-1900 tension)      │     │
│  │  DCA 對象：技術/思想史    │    │  DCA 對象：政治經濟學       │     │
│  │    危機                  │    │    危機                   │     │
│  │                          │    │                          │     │
│  │  狀態：比較層就緒，        │    │  狀態：Phase 2 完成，      │     │
│  │    α₁ 擴充中             │    │    Phase 4-6 待建          │     │
│  └─────────────────────────┘    └─────────────────────────┘     │
│                                                                 │
│  ═══════════════════════════════════════════════════════════    │
│  交叉層（CROSS-CHAMBER.md，待建）                                 │
│  ├── 共享 α（真實歷史）的數據源與 Schema                          │
│  ├── 跨院頻譜比較（ha_ecc vs ha_mecw vs zg vs tt）              │
│  ├── 方法論演進的聯合決策                                        │
│  └── 多世界線擴展的啟動條件                                      │
│  ═══════════════════════════════════════════════════════════    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、共享方法論基礎設施

兩院共享 `system-template/` 及其擴展。任一院的改進可被另一院繼承。

| 資產 | 來源 | 當前狀態 | 備註 |
|:---|:---|:---:|:---|
| `system-template/extensions/ternary/` | ECC | ✅ v3.5 | 兩院通用 |
| `system-template/extensions/soviet/` | ECC | ✅ v3.5 | 兩院通用 |
| `system-template/extensions/spectrum/` | ECC | ✅ v3.5 | 兩院通用，含 mood-valence-map-v3.0.json |
| `system-template/extensions/construct-characters/` | ECC | ✅ v1.0 | ECC 專用（漣漪角色推導） |
| DCA 方法論（六維標準） | ECC KNOWLEDGE-AGENT.md | ✅ v3.0 | 兩院通用 |
| DCA 寫作模板 | ECC docs/manuals/DCA-TEMPLATE.md | ✅ v3.0 | 兩院通用（改寫 ecc_relevance → 改寫 crisis_diagnosis） |
| ADI v4.0 審計腳本 | ECC scripts/audit-knowledge-adi-v4.py | ✅ 就緒 | 兩院通用（換知識庫目錄即可） |
| HISTORICAL-FACT Schema | ECC HISTORICAL-FACT-SCHEMA.md | ✅ v1.0 | 兩院通用 |
| bulk-ingest 管線 | ECC scripts/bulk-ingest-historical-facts.py | ✅ 運作中 | 兩院通用（換 CMH 卷即可） |
| Butterworth 頻譜引擎 | ECC scripts/build-narrative-spectrum.py | ✅ v3.5 | 兩院通用（換信號源即可） |
| percentile-rank divergence | ECC scripts/generate-spectrum-flags.py | ✅ v3.5 | 兩院通用 |
| residual-archaeology.py | MECW-index scripts/ | ✅ v1.0 | 當前 MECW 專用；ECC 可用於 divergent 場景的二次分析 |

---

## 三、統合進度看板

### 3.1 第一院：ECC

| 模組 | 狀態 | 阻擋 | 預計完成 |
|:---|:---:|:---|:---|
| α₁ 事實基線擴充（CMH 第 19-25 章） | 🔄 進行中 | 無 | 2026-06 上旬 |
| α₂ ADI v4.0 全庫評分 | ⬜ 就緒 | P0-1 完成後可並行 | 2026-06 中旬 |
| 比較層 DCA ternary 審計（452 divergent） | ⬜ 就緒 | P0-1 + P0-2 | 2026-06 下旬 |
| v4.0 路線圖（Hilbert 2D 等） | ⬜ 研究級 | 無 | 2026 Q3 |

### 3.2 第二院：MECW-index

| 模組 | 狀態 | 阻擋 | 預計完成 |
|:---|:---:|:---|:---|
| Phase 2: 基礎索引（compiled-documents.json） | ✅ 完成 | 無 | — |
| Phase 3: 人物/地點索引 | ⬜ 待啟動 | 無 | 2026-06 |
| Phase 4: DCA 深度分析（試點 139 篇已完成，待擴展） | 🔄 試點 | DCA 模板需從 ECC 移植 | 2026 Q3 |
| Phase 4b: 歷史事實基線（CMH 1830-1900） | ⬜ 待啟動 | **需等待 ECC 的管線驗證完成** | 2026-07 |
| Phase 6: 頻譜分析（雙變數：ha_MECW vs tt） | ⬜ 待啟動 | Phase 4b 完成 | 2026 Q3 |
| CROSS-CHAMBER.md | ⬜ 待建 | 兩院頻譜均就緒後 | 2026 Q3 |

### 3.3 跨院聯合優先級

```
當前（2026-06）：
  ECC α₁ 擴充（CMH 第 19-25 章）
    │
    ├── 產出：ha 覆蓋率達標 + 管線驗證
    │
    ├──→ ECC P1: DCA ternary 審計
    │
    └──→ MECW Phase 4b: 移植管線，攝取 CMH 1830-1900 卷
              │
              └──→ MECW Phase 6: 頻譜比較（ha_MECW vs tt）
                       │
                       └──→ CROSS-CHAMBER.md: 跨院頻譜比較
```

---

## 四、跨院共享的 α（真實歷史）數據源

兩院目前使用不同的真實歷史數據源，但它們來自同一套學術書：

| 數據 | 時間段 | 使用者 | 狀態 |
|:---|:---|:---|:---:|
| CMH 第 1-18 章（1900-1920） | 1900–1920 | ECC α₁ | ✅ 61 篇，205 events |
| CMH 第 19-25 章（1900-1920 剩餘） | 1900–1920 | ECC α₁ | 🔄 進行中 |
| CMH 1830-1900 卷 | 1830–1900 | MECW α₁（未來） | ⬜ 待 ECC 管線驗證後移植 |

**共享優勢**：同一套 Schema（HISTORICAL-FACT-SCHEMA.md v1.0）、同一套腳本（`bulk-ingest-historical-facts.py`）、同一套時間序列輸出格式（`historical-atmosphere.json`）。MECW 側只需要換 CMH 卷，不需要重新開發。

---

## 五、方法論演進的聯合決策

### 5.1 當前方法論版本鎖定

| 方法論組件 | 版本 | 兩院狀態 |
|:---|:---|:---|
| DCA 寫作公式 | v3.0（危機→滯後→替代→方向） | ✅ 鎖定，兩院通用 |
| DCA 六維標準 | v3.0 | ✅ 鎖定，兩院通用 |
| ADI 審計 | v4.0（結構特徵檢測） | ✅ 鎖定，兩院通用 |
| 頻譜分解 | v3.5（1D Butterworth） | ✅ 鎖定，兩院通用 |
| 比較方法 | v3.5（percentile-rank divergence） | ✅ 鎖定，兩院通用 |
| 比較類型學 | PLAN §13（Vygotsky 單位分析法） | ✅ 鎖定，兩院通用 |

### 5.2 v4.0 升級的跨院影響

任一院的 v4.0 升級（Hilbert 2D 螺旋、Spectral Action）將同時影響兩院，因為頻譜引擎是共享的。v4.0 升級必須滿足：

1. 在 ECC 側完成 A/B 比較（新方法 vs v3.5 基準）
2. 向後兼容——v3.5 的 1D 頻譜數據不丟失
3. 兩院同時升級，保持比較層的一致性

---

## 六、聯合任務日誌

### 2026-06-01

| 時間 | 事件 | 影響範圍 |
|:---|:---|:---|
| — | ECC GRANDPLAN.md v1.0 確認（雙世界線架構） | ECC |
| — | 建立本文件（Grand-unifying-plan&tasklog.md） | 兩院 |
| — | 確認兩院管線依賴：ECC α₁ 擴充 → MECW Phase 4b | 兩院 |
| — | MECW-index GRANDPLAN.md v0.1 識別為待升級（需引入雙世界線架構） | MECW |

### 待辦

| # | 任務 | 負責 | 優先級 |
|:--|:---|:---|:---:|
| 1 | 將 MECW-index GRANDPLAN.md 從 v0.1 線性 Phase 列表升級為雙世界線架構 | 人類 + Opus | 🟡 P1 |
| 2 | 執行 ECC α₁ 擴充（CMH 第 19-25 章） | Copilot | 🔴 P0 |
| 3 | 建立 CROSS-CHAMBER.md（跨院協調委員會） | 人類 + Opus | 🟡 P1 |
| 4 | 確認 MECW-index 的 system-template/ 是否與 ECC 同步 | Copilot | 🟢 P2 |

---

## 七、版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| v1.0 | 2026-06-01 | 初始版本。建立兩院制全景、共享基礎設施清單、統合進度看板、跨院依賴鏈、聯合任務日誌 |
