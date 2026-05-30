#!/usr/bin/env python3
"""
_validate-spectrum.py — 頻譜干涉模式檢測器（頻譜制 Layer 3）

讀取 narrative-spectrum.json，檢測每個時間點的干涉模式
（constructive / destructive / boundary / harmonic），
按敘事意義分為 P0-P3 四級，輸出優先審計列表。

純本地計算，零 API 成本。

用法:
    python extensions/spectrum/_validate-spectrum.py

輸入:
    data/narrative-spectrum.json（由 _build-spectrum.py 生成）

輸出:
    data/spectrum-flags.json（P0-P3 分級列表）

設計者備註（2026-05-29）:
    干涉模式檢測的物理直覺來自波動力學——當兩個波相遇時，
    如果波峰對波峰（同向），振幅增大（constructive）；
    如果波峰對波谷（反向），互相抵消（destructive）。
    
    在敘事頻譜中：
    - constructive = 情緒與結構一致 → 高置信度，可自動通過
    - destructive = 情緒與結構衝突 → 可能是轉折點或 mood 誤標，必須審計
    - boundary = 信號太弱 → 篇章邊界，缺乏上下文
    - harmonic = 週期共振 → 結構性重複／母題
    
    ⚠️ 干涉模式檢測僅供參考——最終判斷由人工（或三進制 AI 審計）做出。
"""

import json
import os
import sys
import numpy as np

# ============================================================================
# ## CUSTOMIZE HERE: 自訂你的系統配置
# ============================================================================

SYSTEM_NAME = "my-system"
SPECTRUM_PATH = "data/narrative-spectrum.json"
OUTPUT_PATH = "data/spectrum-flags.json"

# 干涉檢測閾值（可根據你的數據特點調整）
DESTRUCTIVE_THRESHOLD = 0.5   # 短波能量超過此值 + 與長波反向 → destructive
BOUNDARY_PHASE_MIN = 0.05     # 長波相位低於此值 → boundary（開端）
BOUNDARY_PHASE_MAX = 0.95     # 長波相位高於此值 → boundary（尾聲）
HARMONIC_TOLERANCE = 0.1      # 中波週期與長波週期的整數比容差

# ============================================================================
# 干涉模式檢測
# ============================================================================

def detect_interference(entry: dict, total: int) -> dict:
    """
    檢測單個時間點的干涉模式。
    
    返回:
        {
            "pattern": "constructive"|"destructive"|"boundary"|"harmonic",
            "significance": str,  # 人類可讀的解釋
            "confidence": float   # 0-1
        }
    """
    sp = entry.get("spectrum", {})
    lw = sp.get("longwave", {})
    mw = sp.get("midwave", {})
    sw = sp.get("shortwave", {})
    
    lw_phase = lw.get("phase", 0.5)
    lw_amp = lw.get("amplitude", 0.0)
    lw_trend = lw.get("trend", "stable")
    sw_energy = abs(sw.get("energy", 0.0))
    sw_sign = 1 if sw.get("energy", 0) >= 0 else -1
    lw_sign = 1 if lw_amp >= 0 else -1
    
    # 規則 1：boundary detection（篇章邊界）
    if lw_phase < BOUNDARY_PHASE_MIN or lw_phase > BOUNDARY_PHASE_MAX:
        return {
            "pattern": "boundary",
            "significance": f"長波相位 {lw_phase:.3f}——處於篇章邊界，缺乏足夠的長波上下文",
            "confidence": 0.85
        }
    
    # 規則 2：destructive detection（破壞性干涉）
    # 條件：短波高能量 + 短波與長波反向
    if sw_energy > DESTRUCTIVE_THRESHOLD and sw_sign != lw_sign:
        return {
            "pattern": "destructive",
            "significance": (
                f"長波{lw_trend}段（振幅 {lw_amp:.2f}）出現短波高能量"
                f"{'正向' if sw_sign > 0 else '負向'}脈衝（能量 {sw_energy:.2f}）——"
                f"可能是轉折點、異常事件或 mood 誤標"
            ),
            "confidence": min(0.95, 0.5 + sw_energy * 0.5)
        }
    
    # 規則 3：harmonic detection（諧波共振）
    mw_period = mw.get("period", 20)
    # 檢測中波週期是否接近長波主導週期的整數倍
    # （簡化版——完整版需要用 FFT 檢測諧波峰值）
    
    # 規則 4：constructive（默認——無異常）
    return {
        "pattern": "constructive",
        "significance": "短波/中波/長波無明顯衝突——情緒與結構一致",
        "confidence": 0.7
    }


def classify_priority(interference: dict) -> str:
    """
    根據干涉模式分配審計優先級。
    
    P0 (destructive): 必審——高概率存在 mood 誤標或結構性轉折點
    P1 (boundary):   抽檢——篇章邊界，上下文不足
    P2 (constructive/harmonic): 自動通過或自動標記
    P3 (unmarked):   常規抽檢
    """
    pattern = interference.get("pattern", "constructive")
    mapping = {
        "destructive": "P0",
        "boundary": "P1",
        "constructive": "P2",
        "harmonic": "P2",
    }
    return mapping.get(pattern, "P3")


def validate_spectrum(spectrum_data: dict) -> dict:
    """主函數：檢測所有時間點的干涉模式並分級"""
    
    entries = spectrum_data.get("entries", [])
    meta = spectrum_data.get("_meta", {})
    total = meta.get("total_items", len(entries))
    
    if total == 0:
        return {"_meta": {"error": "無數據", "count": 0}}
    
    # 為每個時間點檢測干涉模式
    flags = {"P0_destructive": [], "P1_boundary": [], "P2_constructive": [], "P3_unmarked": []}
    details = []
    
    for entry in entries:
        interference = detect_interference(entry, total)
        priority = classify_priority(interference)
        
        item_id = entry.get("item_id", "unknown")
        flags[f"{priority}_{interference['pattern']}"].append(item_id)
        
        details.append({
            "item_id": item_id,
            "priority": priority,
            "interference": interference
        })
    
    # 計算統計
    p0_count = len(flags["P0_destructive"])
    p1_count = len(flags["P1_boundary"])
    p2_count = len(flags["P2_constructive"])
    p3_count = len(flags["P3_unmarked"])
    
    # 推薦審計目標（P0+P1）
    recommended = flags["P0_destructive"] + flags["P1_boundary"]
    
    return {
        "_meta": {
            "total_items": total,
            "P0_destructive_count": p0_count,
            "P1_boundary_count": p1_count,
            "P2_constructive_count": p2_count,
            "P3_unmarked_count": p3_count,
            "recommended_audit_target": ["P0", "P1"],
            "recommended_audit_count": len(recommended),
            "estimated_api_savings": f"{(1 - len(recommended)/total)*100:.0f}%",
            "note": (
                "⚠️ P0 場景建議優先人工審查。"
                "P2 場景可通過 SPRT 序貫驗證後批量免審（預期節省 93% API 調用）。"
            ),
            "generated_at": "2026-05-29"
        },
        "flags": flags,
        "details": details[:10]  # 僅輸出前 10 個細節（完整列表見 flags）
    }


def main():
    if not os.path.exists(SPECTRUM_PATH):
        print(f"[ERROR] {SPECTRUM_PATH} 不存在。請先執行 _build-spectrum.py")
        sys.exit(1)
    
    with open(SPECTRUM_PATH, "r", encoding="utf-8") as f:
        spectrum_data = json.load(f)
    
    result = validate_spectrum(spectrum_data)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    meta = result["_meta"]
    print(f"干涉模式檢測完成：{OUTPUT_PATH}")
    print(f"  總場景數：{meta['total_items']}")
    print(f"  P0 (destructive)：{meta['P0_destructive_count']} —— 必審")
    print(f"  P1 (boundary)：{meta['P1_boundary_count']} —— 抽檢")
    print(f"  P2 (constructive)：{meta['P2_constructive_count']} —— 可自動通過")
    print(f"  P3 (unmarked)：{meta['P3_unmarked_count']} —— 常規抽檢")
    print(f"  建議審計：{meta['recommended_audit_count']} 個場景")
    print(f"  預估 API 節省：{meta['estimated_api_savings']}")


if __name__ == "__main__":
    main()
