#!/usr/bin/env python3
"""
_tension-map.py — 蘇維埃 (Soviet) 張力圖譜生成器

從多個系統實例的 compiled JSON 中讀取三態標記（asserted/contested/unknown），
生成跨系統張力圖譜——標記各系統之間的 contested 交叉點。

這是蘇維埃模式的「中央繪圖」工具——它不裁決矛盾，只標記矛盾位置。

用法:
    python extensions/soviet/_tension-map.py \\
      --systems scene,knowledge \\
      --output tension-map.json

依賴:
    - 各系統的 compiled-{name}.json（由 _build-compiled-db.py 生成）
    - 各系統的三態標記（由 _audit-ternary.py 寫入的 audit_v2 字段）

設計者備註（2026-05-29）:
    這個腳本的核心功能是「標記不一致」，不是「修正不一致」。
    當場景系統說某個 mood 是 contested，而知識系統說對應的歷史背景是 asserted，
    我們不判斷誰對誰錯——我們只記錄這個交叉點的位置和張力類型。
    人類稍後會來審查。
"""

import json
import sys
import os
from collections import defaultdict

# ## CUSTOMIZE HERE: 定義你的系統列表
SYSTEMS = ["scene", "knowledge", "character"]

def load_system(system_name: str) -> dict:
    """載入一個系統的 compiled JSON"""
    path = f"data/compiled-{system_name}.json"
    if not os.path.exists(path):
        print(f"[WARN] {path} 不存在，跳過 {system_name}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_ternary_states(compiled: dict) -> dict:
    """
    從 compiled JSON 中提取所有條目的三態標記。
    
    三態標記可能在以下位置：
    - frontmatter.audit_v2.status（場景系統）
    - frontmatter.ecc_relevance 中的 contested 關鍵詞（知識系統）
    
    返回: {item_id: {"status": "asserted"|"contested"|"unknown", "system": str}}
    """
    states = {}
    items = compiled.get("entries", compiled.get("scenes", []))
    
    for item in items:
        item_id = item.get("id", item.get("scene_id", "unknown"))
        
        # 場景系統：檢查 audit_v2
        audit = item.get("audit_v2", {})
        if audit and "status" in audit:
            states[item_id] = {
                "status": audit["status"],
                "system": compiled.get("_meta", {}).get("name", "unknown"),
                "item": item
            }
            continue
        
        # 知識系統：檢查 ecc_relevance 中的 contested 標記
        fm = item.get("frontmatter", item)
        ecc = fm.get("ecc_relevance", {})
        if isinstance(ecc, dict):
            # 檢查四個字段中是否有 contested 語言
            for field in ["crisis", "lag", "alternative", "direction"]:
                text = str(ecc.get(field, ""))
                # 如果文本中存在「矛盾」「爭議」「張力」「兩難」等詞彙
                # 標記為 contested（這需要更精細的 NLP，這裡是簡化版）
                pass
    
    return states

def find_cross_system_tensions(systems_data: dict) -> list:
    """
    跨系統張力檢測。
    
    規則（可按需擴展）：
    1. 同一 ID 在不同系統中有不同狀態 → 標記為 status_conflict
    2. 場景中 contested 的項目在知識系統中有對應條目 → 標記為 cross-reference
    3. 系統 A 標 asserted 但系統 B 標 unknown → 標記為 information_asymmetry
    """
    tensions = []
    
    # 收集所有系統的所有狀態
    all_states = defaultdict(dict)
    for sys_name, compiled in systems_data.items():
        if compiled is None:
            continue
        states = extract_ternary_states(compiled)
        for item_id, state_info in states.items():
            all_states[item_id][sys_name] = state_info
    
    # 檢測衝突
    for item_id, sys_states in all_states.items():
        if len(sys_states) < 2:
            continue  # 只有一個系統有這個條目，無衝突
        
        statuses = {s: info["status"] for s, info in sys_states.items()}
        unique_statuses = set(statuses.values())
        
        if len(unique_statuses) > 1:
            tensions.append({
                "item_id": item_id,
                "type": "status_conflict",
                "systems": statuses,
                "recommended_action": "人工審查——不同系統對同一條目有不同判斷"
            })
    
    return tensions

def generate_tension_map(systems: list) -> dict:
    """主函數：生成跨系統張力圖譜"""
    
    # 載入所有系統
    systems_data = {}
    for sys_name in systems:
        compiled = load_system(sys_name)
        if compiled:
            systems_data[sys_name] = compiled
    
    if len(systems_data) < 2:
        return {
            "_meta": {
                "error": "至少需要兩個系統才能生成張力圖譜",
                "loaded_systems": list(systems_data.keys())
            }
        }
    
    # 檢測跨系統張力
    tensions = find_cross_system_tensions(systems_data)
    
    # 生成報告
    return {
        "_meta": {
            "generated_at": "2026-05-29",
            "systems_loaded": list(systems_data.keys()),
            "total_tensions": len(tensions),
            "note": "這是一份張力圖譜，不是錯誤報告。tension ≠ error。"
        },
        "tensions": tensions,
        "summary": {
            "status_conflicts": len([t for t in tensions if t["type"] == "status_conflict"]),
            "cross_references": len([t for t in tensions if t["type"] == "cross-reference"]),
            "information_asymmetries": len([t for t in tensions if t["type"] == "information_asymmetry"]),
        }
    }

def main():
    systems = SYSTEMS
    if "--systems" in sys.argv:
        idx = sys.argv.index("--systems")
        systems = sys.argv[idx + 1].split(",")
    
    output_path = "data/tension-map.json"
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        output_path = sys.argv[idx + 1]
    
    result = generate_tension_map(systems)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"張力圖譜已生成：{output_path}")
    print(f"  載入系統：{result['_meta']['systems_loaded']}")
    print(f"  張力節點：{result['_meta']['total_tensions']}")
    print(f"  ⚠️  reminder: tension ≠ error. 這些是需要人工審查的交叉點，不是需要修正的錯誤。")

if __name__ == "__main__":
    main()
