#!/usr/bin/env python3
"""
_build-spectrum.py — 敘事頻譜定位系統（頻譜制 Layer 3）

從 compiled JSON 中提取連續時間序列數據（如場景的 mood 數值），
用 Butterworth 濾波器分解為長波/中波/短波三個頻段，
為每個時間點輸出精確的頻譜坐標（相位、振幅、趨勢）。

純本地計算（NumPy/SciPy），零 API 成本，1,339 場景 < 100ms。

用法:
    python extensions/spectrum/_build-spectrum.py

依賴:
    pip install numpy scipy

輸入:
    data/compiled-{name}.json（由 _build-compiled-db.py 生成）

輸出:
    data/narrative-spectrum.json

設計者備註（2026-05-29）:
    頻譜層的靈感：LLM 的注意力機制是 flat 的——它不知道「第 47 場景在整個故事中
    處於什麼位置」。Transformer 沒有內建的時間感知。頻譜層用最便宜的本地 FFT
    補上這個維度，然後把坐標注入 AI 的 Prompt——讓 AI 在「GPS 定位」後再做判斷。
    
    ⚠️ 阿基里斯腱：mood→數值的映射。如果映射是主觀的，頻譜輸出就不是敘事結構
    而是映射者的審美偏好。Phase 1 實驗必須先驗證這個映射的客觀性。
"""

import json
import os
import sys
import numpy as np

# 嘗試導入 scipy（可選依賴）
try:
    from scipy import signal
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("[WARN] scipy 未安裝。頻譜分解功能不可用。請執行: pip install scipy")
    print("[INFO] 將使用簡化的移動平均作為替代（精度較低）")

# ============================================================================
# ## CUSTOMIZE HERE: 自訂你的系統配置
# ============================================================================

SYSTEM_NAME = "my-system"
DB_PATH = f"data/compiled-{SYSTEM_NAME}.json"
OUTPUT_PATH = "data/narrative-spectrum.json"

# ## CUSTOMIZE HERE: mood→數值映射表
# 這是最關鍵的部分。以下映射僅為示例——必須通過實驗校準。
# 校準方法：三人獨立映射 50 個場景 → 比較 FFT 輸出 → 如不一致則降級。
MOOD_VALENCE_MAP = {
    # 正向情緒（>0）
    "exuberant": 0.9,
    "hopeful": 0.7,
    "tender": 0.6,
    "calm": 0.4,
    "nostalgic": 0.2,
    "curious": 0.3,
    "warm": 0.5,
    
    # 中性（≈0）
    "neutral": 0.0,
    "observant": 0.1,
    "resigned": -0.1,
    "pensive": -0.1,
    
    # 負向情緒（<0）
    "melancholic": -0.3,
    "tense": -0.4,
    "somber": -0.5,
    "solemn": -0.6,
    "grieving": -0.7,
    "furious": -0.8,
    "despairing": -0.9,
    "cold": -0.5,
    "distant": -0.4,
}

# ============================================================================
# 核心算法
# ============================================================================

def mood_to_val(mood_str: str) -> float:
    """
    將 mood 字串轉換為數值。
    
    ⚠️ 這是整個頻譜層的阿基里斯腱。
    如果三個獨立映射者用不同的映射產生不同的頻譜，
    則頻譜層的信號品質無法保證——降級為 reference-only。
    """
    if not mood_str:
        return 0.0
    
    mood_str = mood_str.lower().strip()
    
    # 精確匹配
    if mood_str in MOOD_VALENCE_MAP:
        return MOOD_VALENCE_MAP[mood_str]
    
    # 模糊匹配（檢查子字串）
    for key, val in MOOD_VALENCE_MAP.items():
        if key in mood_str or mood_str in key:
            return val
    
    # 默認：中性
    return 0.0


def build_spectrum(compiled_db: dict) -> dict:
    """主函數：計算頻譜坐標"""
    
    entries = compiled_db.get("entries", compiled_db.get("scenes", []))
    
    if len(entries) < 20:
        return {
            "_meta": {
                "error": "數據點不足（需要至少 20 個時間點進行頻譜分解）",
                "count": len(entries)
            }
        }
    
    # 1. 提取數值序列
    values = []
    valid_entries = []
    
    for entry in entries:
        # 嘗試從不同字段提取 mood
        fm = entry.get("frontmatter", entry)
        mood = fm.get("mood", None)
        
        if isinstance(mood, dict):
            # 三進制格式：mood.primary
            mood_str = mood.get("primary", "")
        elif isinstance(mood, str):
            # 二進制格式：直接是字串
            mood_str = mood
        else:
            mood_str = ""
        
        val = mood_to_val(mood_str)
        values.append(val)
        valid_entries.append(entry)
    
    values = np.array(values, dtype=float)
    n = len(values)
    
    # 2. 多尺度分解
    if HAS_SCIPY:
        # === 精確版：Butterworth 濾波器 ===
        
        # 長波：>50 場景週期 → 低通濾波（截止頻率 0.02 = 1/50）
        b_l, a_l = signal.butter(4, 0.02, 'low')
        longwave = signal.filtfilt(b_l, a_l, values)
        
        # 中波：10-50 場景週期 → 帶通濾波（0.02–0.1）
        b_m, a_m = signal.butter(4, [0.02, 0.1], 'band')
        midwave = signal.filtfilt(b_m, a_m, values)
        
        # 短波：殘差
        shortwave = values - longwave - midwave
        
        # FFT 主導週期檢測
        fft = np.fft.rfft(values)
        freqs = np.fft.rfftfreq(n, d=1.0)
        if len(fft) > 1:
            dominant_idx = np.argmax(np.abs(fft[1:])) + 1
            dominant_period = int(1.0 / freqs[dominant_idx]) if freqs[dominant_idx] > 0 else n
        else:
            dominant_period = n
        
        method = "butterworth"
        
    else:
        # === 簡化版：移動平均（不依賴 scipy） ===
        window_l = min(50, n // 4)
        window_m = min(20, n // 8)
        
        longwave = np.convolve(values, np.ones(window_l)/window_l, mode='same')
        midwave = np.convolve(values, np.ones(window_m)/window_m, mode='same') - longwave
        shortwave = values - longwave - midwave
        dominant_period = window_l
        
        method = "moving_average_(scipy_not_installed)"
    
    # 3. 為每個時間點輸出頻譜坐標
    spectrum_entries = []
    for i, entry in enumerate(valid_entries):
        entry_id = entry.get("id", entry.get("scene_id", f"item-{i}"))
        
        # 長波相位：在整個序列中的相對位置（0→1）
        lw_phase = i / n if n > 0 else 0
        lw_amp = float(longwave[i])
        
        # 中波相位：在中波週期中的位置（0→1）
        mid_period = max(dominant_period, 10)
        mw_phase = (i % mid_period) / mid_period if mid_period > 0 else 0
        mw_amp = float(midwave[i])
        
        # 短波能量
        sw_energy = float(shortwave[i])
        sw_class = "spike" if abs(sw_energy) > 0.5 else "noise"
        
        spectrum_entry = {
            "item_id": entry_id,
            "index": i,
            "spectrum": {
                "longwave": {
                    "phase": round(lw_phase, 3),
                    "amplitude": round(lw_amp, 3),
                    "trend": "rising" if (i < n/3) else ("stable" if i < 2*n/3 else "falling")
                },
                "midwave": {
                    "phase": round(mw_phase, 3),
                    "amplitude": round(mw_amp, 3),
                    "period": mid_period
                },
                "shortwave": {
                    "energy": round(sw_energy, 3),
                    "classification": sw_class
                }
            }
        }
        spectrum_entries.append(spectrum_entry)
    
    # 4. 元數據
    return {
        "_meta": {
            "method": method,
            "total_items": n,
            "dominant_period": dominant_period,
            "scipy_available": HAS_SCIPY,
            "mood_valence_map_sample": dict(list(MOOD_VALENCE_MAP.items())[:5]),
            "warning": (
                "⚠️ 頻譜品質取決於 mood→數值映射的客觀性。"
                "如果未經三人獨立映射 FFT 比較校準，頻譜坐標僅供參考。"
            ),
            "generated_at": "2026-05-29"
        },
        "entries": spectrum_entries
    }


def main():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] {DB_PATH} 不存在。請先執行 _build-compiled-db.py")
        sys.exit(1)
    
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    
    result = build_spectrum(db)
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    meta = result["_meta"]
    print(f"頻譜計算完成：{OUTPUT_PATH}")
    print(f"  方法：{meta['method']}")
    print(f"  數據點：{meta['total_items']}")
    print(f"  主導週期：{meta['dominant_period']} 個時間單位")
    print(f"  {meta['warning']}")


if __name__ == "__main__":
    main()
