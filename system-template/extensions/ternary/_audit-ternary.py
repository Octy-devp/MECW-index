#!/usr/bin/env python3
"""
_audit-ternary.py — 三進制審計腳本（可選擴展，Layer 2）

================================================================================
設計背景（為什麼需要這個腳本）
================================================================================

在二進制驗證（Layer 1）的世界中，每個字段只有兩種狀態：
  ✅ mood 標籤存在 → Pass
  ❌ mood 標籤缺失 → Fail

但這無法回答一個更重要的問題：
  「這個 mood 標籤是誠實的嗎？文本中是否存在支持相反判斷的證據？」

三進制審計的任務不是「檢查格式」，而是「顯性化矛盾」：
  - Asserted：文本證據充足且一致 → 高置信度，可自動通過
  - Contested：文本證據存在矛盾 → 標記為需要人工裁定（這是核心價值）
  - Unknown：文本信息不足 → 標記為盲區，等待更多數據

================================================================================
蘇維埃模式在這個腳本中的體現
================================================================================

這個腳本不「裁決」任何東西。它只是一個「觀察員」：
  1. 它讀取文本和（可選的）頻譜坐標
  2. 它調用 AI 做語義判斷
  3. 它輸出三態標記 + 證據摘要
  4. 它從不修改原始條目——所有輸出寫入獨立的 audit 字段

「中央」（AGENTS.md 路由 + 人工審查者）的任務不是推翻這個腳本的判斷，
而是在 contested 節點上做出選擇——而這個腳本的價值恰恰在於：它告訴你
「哪裡需要選擇」。

================================================================================
依賴關係
================================================================================

- 必需：Layer 1（compiled-{name}.json）——用於讀取條目列表
- 可選：Layer 3（spectrum-flags.json）——如果存在，注入頻譜坐標到 Prompt
  如果 spectrum-flags.json 不存在，腳本仍正常運行，只是 Prompt 不含頻譜上下文

================================================================================
用法
================================================================================

# 基本用法（無頻譜層）
python scripts/_audit-ternary.py

# 指定只審計特定分類
python scripts/_audit-ternary.py --cat cat-a

# 指定只審計 P0+P1 場景（需要先跑 spectrum）
python scripts/_audit-ternary.py --flags data/spectrum-flags.json

# 試運行（不調用 API，僅顯示將審計哪些條目）
python scripts/_audit-ternary.py --dry-run
"""

import json, sys, os, re
from pathlib import Path

# ============================================================================
# 配置區 —— 使用前必須修改
# ============================================================================

# 你的系統名稱（與 _build-compiled-db.py 中的 SYSTEM_NAME 一致）
SYSTEM_NAME = "my-system"

# 編譯庫路徑（由 Layer 1 的 _build-compiled-db.py 生成）
DB_PATH = f"data/compiled-{SYSTEM_NAME}.json"

# 頻譜標記文件路徑（可選——由 Layer 3 的 _validate-spectrum.py 生成）
# 如果此文件不存在，腳本仍正常運行，只是 Prompt 不含頻譜坐標
SPECTRUM_FLAGS_PATH = "data/spectrum-flags.json"

# raw 條目目錄（用於讀取完整文本做語義審計）
RAW_DIR = "raw"

# ============================================================================
# 三進制 Prompt 模板
# ============================================================================
# 
# 設計說明：
# 這個 Prompt 的核心設計原則是「閹割敘事衝動」——
# 明確禁止 AI 輸出因果解釋、成長軌跡、連續敘事。
# AI 只能輸出：看到了什麼、有多大把握、有什麼反證。
# 
# 為什麼要這樣？因為級聯失真的根源就是：
# 基層 AI 在證據不足時，用「聽起來合理的故事」填補空白。
# 上層 AI 收到這個故事後，把它當做事實繼續往下傳。
# 三進制 Prompt 的任務就是打斷這個鏈條——在基層就阻止敘事衝動。

TERNARY_PROMPT_TEMPLATE = """你是一個嚴格的文本審計員。你的任務不是「講故事」，而是「標註認知狀態」。

## 審計對象
- 條目 ID：{entry_id}
- 條目標題：{title}
- 條目內容：
{content}

{spectrum_section}

## 你的任務

對以下字段進行三進制判斷（每個字段獨立判斷）：

{target_fields}

## 三態定義（嚴格遵守）

1. **Asserted**（已確證）
   - 定義：文本中有 ≥3 處獨立證據支持該判斷，且無同等強度的反證
   - 輸出格式：`status: asserted`，附上至少 3 個文本錨定（原文引用 + 行號）

2. **Contested**（有爭議）
   - 定義：文本中存在支持該判斷和反對該判斷的**同等強度**證據
   - 這是一個正向認知狀態——不是「我不確定」，而是「我確定文本中有矛盾」
   - 輸出格式：`status: contested`，列出正反雙方證據，標記矛盾點

3. **Unknown**（未知）
   - 定義：文本信息不足以做出判斷（<2 處相關文本，或相關文本支持度均 <0.5）
   - 輸出格式：`status: unknown`，說明缺失什麼信息

## 嚴格禁止

- 禁止輸出「因果解釋」（如「因為...所以...導致了...」）
- 禁止輸出「成長軌跡」（如「從 XX 逐漸轉變為 YY」）
- 禁止輸出「辯證統一」（如「矛盾地統一了 A 與 B」）
- 禁止在證據不足時編造敘事來填補空白
- 禁止將 contested 強行調和為 asserted

## 輸出格式

對每個目標字段，輸出：

```yaml
<field_name>:
  primary: "<你的主要判斷>"
  valence: <0.0~1.0>
  status: <asserted|contested|unknown>
  anchors:
    - quote: "<原文引用>"
      support: <0.0~1.0>
  dissent:  # 僅在 status=contested 時輸出
    - position: "<反方立場>"
      evidence: ["<原文引用>"]
      strength: <0.0~1.0>
  synthesis: null  # 永遠是 null——你不被允許做綜合判斷
```
"""


def load_db():
    """載入編譯庫（Layer 1 產物）"""
    if not os.path.exists(DB_PATH):
        print(f"❌ 編譯庫不存在：{DB_PATH}")
        print(f"   請先執行：python scripts/_build-compiled-db.py")
        sys.exit(1)
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_spectrum_flags():
    """
    載入頻譜標記（Layer 3 產物，可選）
    
    設計說明：
    這是「軟依賴」的實現——如果頻譜文件不存在，函數返回 None，
    後續 Prompt 中的 spectrum_section 為空字符串。
    AI 在沒有頻譜坐標的情況下仍能工作，只是失去了「時間定位」。
    """
    if not os.path.exists(SPECTRUM_FLAGS_PATH):
        return None
    with open(SPECTRUM_FLAGS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_spectrum_section(entry_id, flags):
    """
    為 Prompt 構建頻譜上下文段落
    
    設計說明：
    頻譜坐標的注入不是「告訴 AI 答案」，而是「給 AI 一個 GPS」。
    AI 仍然自己做語義判斷，但現在它知道這個條目在整體結構中的位置——
    長波趨勢是什麼、中波處於什麼階段、短波是否有異常脈衝。
    這讓 AI 從「憑感覺判斷」變成「在坐標上判斷」。
    """
    if not flags:
        return ""
    
    # 查找該條目的頻譜標記
    entry_flag = None
    for priority in ['P0_destructive', 'P1_boundary', 'P2_constructive', 'P3_unmarked']:
        if entry_id in flags.get(priority, []):
            entry_flag = priority
            break
    
    if not entry_flag:
        return ""
    
    return f"""
## 頻譜上下文（由本地頻譜引擎提供）

該條目在整體結構中的頻譜定位：
- 干涉模式：{entry_flag}
- 含義：{'長波與短波衝突，可能存在情緒誤標或轉折點' if 'P0' in entry_flag else '篇章邊界，上下文不足' if 'P1' in entry_flag else '頻譜共振，情緒與結構一致' if 'P2' in entry_flag else '無特殊標記'}

請在審計時特別注意：頻譜提示的可能異常與你的文本分析是否一致。
如果不一致（例如頻譜顯示 destructive 但你認為文本證據充足），
請在輸出中明確指出這一張力——這本身就是有價值的信息。
"""


def call_ai_audit(entry, flags):
    """
    調用 AI 做三進制審計
    
    設計說明：
    這裡是佔位函數。實際實現取決於你使用的 AI API。
    對於 ECC 專案，我們使用 DeepSeek V4-Pro API。
    對於你自己的系統，替換為你使用的 API 調用。
    
    關鍵：AI 的輸出必須是結構化 YAML，而不是自由文本。
    如果 AI 返回自由文本，你需要額外的解析層——
    但這會引入新的不確定性。建議在 Prompt 中嚴格要求 YAML 輸出。
    """
    # === 構建 Prompt ===
    spectrum_section = build_spectrum_section(entry['id'], flags)
    
    # 讀取原始條目內容
    raw_path = os.path.join(RAW_DIR, f"{entry['id']}.md")
    if os.path.exists(raw_path):
        with open(raw_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = str(entry.get('summary', '(無法讀取原始內容)'))
    
    prompt = TERNARY_PROMPT_TEMPLATE.format(
        entry_id=entry['id'],
        title=entry.get('title', '(無標題)'),
        content=content[:5000],  # 截斷以避免超出 token 限制
        spectrum_section=spectrum_section,
        target_fields="mood, analysis"  # 可配置：要審計哪些字段
    )
    
    # === 調用 AI API（佔位——替換為你的實現） ===
    # TODO: 替換為實際的 API 調用
    # result = your_ai_api.call(prompt)
    # return parse_ternary_output(result)
    
    print(f"  [DRY RUN] 將審計：{entry['id']}")
    print(f"  [DRY RUN] Prompt 長度：{len(prompt)} 字符")
    return None


def main():
    """主函數"""
    # 解析命令行參數
    dry_run = '--dry-run' in sys.argv
    use_flags = '--flags' in sys.argv
    
    print("=" * 60)
    print("三進制審計腳本（Layer 2）")
    print("=" * 60)
    print()
    
    # 載入數據
    db = load_db()
    entries = db.get('entries', [])
    print(f"已載入 {len(entries)} 個條目")
    
    flags = None
    if use_flags:
        flags = load_spectrum_flags()
        if flags:
            p0 = len(flags.get('P0_destructive', []))
            p1 = len(flags.get('P1_boundary', []))
            print(f"已載入頻譜標記：P0={p0}, P1={p1}")
            # 只審計 P0 + P1（高優先級場景）
            target_ids = set(flags.get('P0_destructive', []) + flags.get('P1_boundary', []))
            entries = [e for e in entries if e['id'] in target_ids]
            print(f"篩選後審計目標：{len(entries)} 個條目（僅 P0+P1）")
        else:
            print("⚠️ 頻譜標記文件不存在，將審計所有條目（無頻譜上下文）")
    
    print()
    
    # 審計每個條目
    # 
    # 設計說明：
    # 大規模審計時，這裡應該使用批次處理 + SPRT 序貫抽樣來最小化 API 調用。
    # 詳見 recommendation-tsalc-spectrum-architecture.md § 四。
    # 這裡為簡潔起見，展示逐個審計的基本流程。
    
    if dry_run:
        print(f"[DRY RUN 模式] 將審計 {len(entries)} 個條目，不調用 API")
        for entry in entries[:5]:  # 只展示前 5 個
            call_ai_audit(entry, flags)
        if len(entries) > 5:
            print(f"  ... 及其餘 {len(entries) - 5} 個條目")
    else:
        print("⚠️ 實際審計需要配置 AI API。請編輯此腳本的 call_ai_audit() 函數。")
        print("   目前僅支援 --dry-run 模式。")
    
    print()
    print("=" * 60)
    print("審計完成。")
    print()
    print("下一步：")
    print("  1. 審查 contested 條目（人工裁定）")
    print("  2. 對 unknown 條目補充數據或標記為「待補充」")
    print("  3. 將審計結果回寫到 raw/*.md 的 audit_v2 字段")
    print("=" * 60)


if __name__ == '__main__':
    main()
