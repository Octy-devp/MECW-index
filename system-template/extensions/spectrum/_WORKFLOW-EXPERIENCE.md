# ECC 頻譜建置完整經驗模板

> **版本**：v1.0  
> **日期**：2026-05-30  
> **用途**：記錄 Stage 7e/7f 從零到完整三進制審計的完整工作流、經驗教訓、與可複用模板  
> **適用場景**：任何需要對敘事文本進行多尺度頻譜分析 + 三進制語義審計的專案

---

## 一、整體流程（5 Steps）

```
Step 1: MOOD_VALENCE_MAP 設計與校準
  ├── 1.1 提取原型映射表（system-template）
  ├── 1.2 70% 真實歷史基準 + 30% ECC 世界觀偏移（DeepSeek 雙重校準）
  ├── 1.3 2D 向量（valence × arousal）取代 1D 線性軸
  ├── 1.4 Weber 理想型方法論：數值是「測量基準」非「事實描述」
  └── 1.5 容忍度區間（Trotky 辯證法）：何時 A ≠ A
       ↓
Step 2: 三軌頻譜計算
  ├── 2.1 zeitgeist 軌：valence → Butterworth 低通（>50 場景）→ 長波
  ├── 2.2 atmosphere 軌：valence → Butterworth 帶通（10-50 場景）→ 中波
  ├── 2.3 干涉檢測：P0 destructive / P1 boundary / P2 constructive / P3 unmarked
  └── 2.4 可視化 + 檔案歸檔
       ↓
Step 2.5: 四方法統計驗證
  ├── Fisher ANOVA F-test：篇章間情緒差異是否顯著
  ├── Pearson χ²：篇章是否有獨特情緒指紋
  ├── 蘇聯物質平衡：情緒流動矩陣（可選）
  └── Tchuprow-Neyman 分層抽樣：最適審計資源分配
       ↓
Step 3 (7e-3): char_arc 角色成長軌
  ├── A/B test 方案比較（5 輪，6 方案）
  ├── 選定方案：B-Rich（5 維結構化輸出）
  └── P0 場景優先 → P1 場景擴展
       ↓
Step 4 (7f): 三進制語義審計
  ├── P0 → contested（強制）
  ├── P1 → unknown（邊界，缺乏上下文）
  ├── P2+P3 → asserted（自動通過）
  └── 人工審查 contested 清單
```

---

## 二、關鍵經驗教訓

### 2.1 Gemini Flash 分工邊界

| ✅ 給 Gemini | ❌ 不給 Gemini |
|:---|:---|
| 用**給定的** MOOD_VALENCE_MAP 計算頻譜 | 自行設計或簡化映射表 |
| 寫 Butterworth/FFT 計算腳本 | 判斷情緒極性（正/負） |
| 批量數據處理 + 可視化 | 解釋頻譜的敘事意義 |
| 生成 P0-P3 預警 | 最終裁定 contested |

**核心教訓**：Gemini 是極高效的建造者，不是可靠的判斷者。所有需要方法論判斷的環節（映射設計、極性判定、校準）必須由 Copilot/DeepSeek 或人類完成。

### 2.2 atmosphere 軌的陷阱

**v3.0 失敗**：用關鍵詞提取法從 `mood_description`（文學性文本）提取 atmosphere 信號 → 全部均值接近 0.0，完全平坦。

**v3.1 修正**：atmosphere 不用獨立信號源。直接使用與 zeitgeist 相同的 valence 信號，但用不同濾波器（帶通 [0.04, 0.1]）分離時間尺度。這是標準的多尺度分解——同一信號源，不同頻率分量。

**教訓**：文學性文本不適合關鍵詞提取。數學分解比 NLP 更可靠。

### 2.3 過度篇（低信號篇章）的處理

84% 場景的 mood 未在映射表中。三種處理方案的優劣：

| 方案 | 做法 | 結果 |
|:---|------|------|
| ❌ 均值填充（0.0） | 未映射 → 填 0.0 | Butterworth 產生虛假趨勢 |
| ❌ 擴表 | 補齊所有缺失 mood | 不實際（需 50+ 詞） |
| ✅ **線性插值** | 從相鄰篇章邊界值線性插值 | 保留信號連續性，標記 unreliable |

### 2.4 char_arc 的 A/B Test 教訓

**關鍵發現**：LLM 對「給一個數字」的任務存在內在不穩定性。同一場景（scene-174），方案 A（Direct）給 +0.35，方案 B（Rich）給 -0.30——完全相反的 valence。

**解決方案**：char_arc 不能只輸出一個數字。必須使用結構化多維輸出（valence + arousal + conflict_mood + conflict_zeitgeist + emotion），以多維度交叉驗證防止單點不穩定。

### 2.5 70/30 雙變異數比較框架

MOOD_VALENCE_MAP 的基準不是憑空想像，而是雙重校準：

$$\vec{V}_{comparison} = (\sigma^2_{ECC} - \sigma^2_{history},\quad \mu_{ECC} - \mu_{history})$$

- 70%：從知識庫（knowledge-raw）提取真實歷史 1900-1920 的情緒結構
- 30%：ECC 世界觀對歷史的改寫（無世界大戰、家庭保留、革命路徑不同）

---

## 三、可複用模板

### 3.1 Gemini 頻譜計算 Prompt 模板

```markdown
## 任務：頻譜計算

### 輸入
- `data/compiled-{name}.json`：場景數據
- `extensions/spectrum/mood-valence-map-v3.0.json`：已校準的 2D 向量表

### 要做的事
1. 對每個場景，從 mood 字段查找映射表中的 valence 值
2. 未映射場景用該篇章的已映射均值填充（不要填 0.0）
3. 按篇章分組，做 Butterworth 4 階濾波：
   - 長波（zeitgeist）：低通，截止頻率 0.04
   - 中波（atmosphere）：帶通 [0.04, 0.1]
4. 干涉檢測：zeitgeist 與 atmosphere 符號相反且 |atmosphere| > 0.3 → P0 destructive
5. 生成可視化圖

### 🚫 不許做的事
- 不許修改映射表
- 不許用關鍵詞提取取代數學濾波
- 不許將未映射場景填 0.0
- 不許自行判斷情緒極性
```

### 3.2 char_arc B-Rich Prompt 模板

```markdown
## 任務：角色視角情緒分析

場景：{scene_id} | mood={mood} | zeitgeist={z_val} | atmosphere={a_val}

從{primary_character}的視角，輸出 ONLY（不解釋）：
valence: <float -1 to +1>
arousal: <float 0 to 1>
conflict_mood: <true/false>
conflict_zeitgeist: <true/false>
emotion: <1 word>

場景文本：{text}
```

### 3.3 Neyman 最適分配公式

$$n_h = n \cdot \frac{N_h \sigma_h}{\sum_{k} N_k \sigma_k}$$

注意：分子是 **σ（標準差）**，不是 σ²（變異數）。用 σ² 會過度懲罰高變異篇章。

### 3.4 檔案歸檔規範

```
index/data/
├── narrative-spectrum-v{version}.json    ← 頻譜數據
├── spectrum-flags-v{version}.json        ← P0-P3 分級
├── char-arc-p0-pilot.json                ← char_arc 分析
├── audit-ternary-v{version}.json         ← 三進制審計
└── longwave-trend-v{version}.png         ← 可視化

.taskbook/reports/spectrum-v{old}-archive/ ← 歷史版本歸檔

scripts/
├── build-narrative-spectrum.py           ← 頻譜計算（支援 --plot-only）
├── spectrum-validator.py                 ← 干涉檢測
└── run-step2.py                          ← 主控腳本
```

---

## 四、完整數據流

```
compiled-scenes.json
    │
    ├──→ mood-valence-map-v3.0.json (48-mood 2D 向量表)
    │         │
    │         └──→ valence 序列
    │                  │
    │        ┌─────────┴─────────┐
    │        ▼                   ▼
    │   Butterworth 低通     Butterworth 帶通
    │   (zeitgeist 長波)     (atmosphere 中波)
    │        │                   │
    │        └─────────┬─────────┘
    │                  ▼
    │           干涉檢測 (P0-P3)
    │                  │
    │        ┌─────────┼─────────┐
    │        ▼         ▼         ▼
    │      P0         P1       P2+P3
    │   contested   unknown   asserted
    │        │
    │        └──→ char_arc (Copilot/DeepSeek)
    │                  │
    │                  ▼
    │           三進制審計 (audit-ternary-v1.0.json)
    │                  │
    │                  ▼
    │           人工審查 contested
    │                  │
    │                  ▼
    │           GRANDPLAN / TASKLOG 更新
```

---

## 五、最終檢查清單

部署前確認：

- [ ] `mood-valence-map-v3.0.json` 覆蓋率 ≥ 80%
- [ ] ANOVA F-test p < 0.001
- [ ] χ² independence test p < 0.001
- [ ] 過度篇/低信號篇章已標記 unreliable
- [ ] P0 場景已通過人工審查
- [ ] GRANDPLAN.md 狀態已更新
- [ ] TASKLOG.md 狀態已更新
- [ ] AGENTS.md 頻譜文件引用已更新
- [ ] SCHEMA.md 已新增頻譜可選字段
- [ ] 舊版本已歸檔至 `.taskbook/reports/`

---

## 六、版本歷史

| 版本 | 日期 | 內容 |
|------|------|------|
| v1.0 | 2026-05-30 | 初始版本：記錄 Stage 7e/7f 完整經驗，包含所有模板、教訓、檢查清單 |
