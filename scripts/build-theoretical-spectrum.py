#!/usr/bin/env python3
"""
MECW 理論張力頻譜計算器 v0.1
從 keyword-timeseries.json 合成 composite tension index，
Butterworth 分解長波/中波/短波，輸出 theoretical-spectrum.json

複用 ECC 頻譜層的技術棧：
  - Butterworth 4th-order: lowpass(0.04) + bandpass[0.04,0.1]
  - 與 ECC 的 valence → zeitgeist/atmosphere 完全同構

用法：
  python scripts/build-theoretical-spectrum.py
  python scripts/build-theoretical-spectrum.py --plot
"""

import json, os, argparse
from pathlib import Path
from datetime import datetime
import numpy as np
from scipy import signal
from collections import defaultdict

ROOT = Path(__file__).parent.parent
KEYWORDS_IN = ROOT / "index" / "data" / "keyword-timeseries.json"
COMPILED = ROOT / "index" / "data" / "compiled-documents.json"
SPECTRUM_OUT = ROOT / "index" / "data" / "theoretical-spectrum.json"

# Butterworth 參數（與 ECC 一致）
LOWPASS_CUTOFF = 0.04   # >50 場景週期 → 長波（理論正規化）
BANDPASS_LOW = 0.04     # 10-50 場景週期 → 中波（篇章級張力）
BANDPASS_HIGH = 0.1
FILTER_ORDER = 4

# 關鍵詞權重（基於理論重要性初步賦權，後續可用 ANOVA 校準）
KEYWORD_WEIGHTS = {
    "revolution": 1.5,    # 革命是最高張力信號
    "class": 1.3,         # 階級是核心分析範疇
    "proletariat": 1.2,   # 革命主體
    "capital": 1.1,       # 批判對象
    "communism": 1.4,     # 目標——高張力
    "state": 0.9,         # 中性分析工具
    "labour": 0.8,        # 基礎範疇
    "party": 1.0,         # 組織形式
}

def build():
    # 載入關鍵詞數據
    with open(KEYWORDS_IN, "r") as f:
        kw_data = json.load(f)["keywords"]

    # 載入文獻統計（用於年文獻數正則化）
    with open(COMPILED, "r") as f:
        docs = json.load(f)["documents"]

    # 計算每年文獻數
    docs_per_year = defaultdict(int)
    for d in docs:
        y = d.get("year")
        if y and isinstance(y, int) and 1835 <= y <= 1895:
            docs_per_year[y] += 1

    # 合成 annual tension index
    all_years = set()
    for kw in kw_data.values():
        for pt in kw:
            all_years.add(pt["year"])
    years = sorted(y for y in all_years if 1835 <= y <= 1895)

    tension_series = []
    for year in years:
        composite = 0.0
        for kw, weight in KEYWORD_WEIGHTS.items():
            kw_series = {d["year"]: d["freq_per_10k"] for d in kw_data.get(kw, [])}
            freq = kw_series.get(year, 0)
            composite += freq * weight
        # 正則化：除以當年文獻數（避免文獻多=張力高的偏差）
        n_docs = docs_per_year.get(year, 1)
        tension_series.append({
            "year": year,
            "tension_raw": round(composite, 2),
            "tension_per_doc": round(composite / max(n_docs, 1), 4),
            "documents": n_docs,
        })

    # ── Butterworth 濾波 ──────────────────────────
    n = len(tension_series)
    if n < 10:
        print("Too few data points for Butterworth filtering")
        return

    signal_raw = np.array([d["tension_per_doc"] for d in tension_series])
    nyquist = 0.5  # 歸一化 Nyquist 頻率

    # Lowpass → 長波（理論正規化）
    b_lp, a_lp = signal.butter(FILTER_ORDER, LOWPASS_CUTOFF / nyquist, btype='low')
    longwave = signal.filtfilt(b_lp, a_lp, signal_raw)

    # Bandpass → 中波（篇章級張力波動）
    b_bp, a_bp = signal.butter(FILTER_ORDER,
                                [BANDPASS_LOW / nyquist, BANDPASS_HIGH / nyquist],
                                btype='band')
    midwave = signal.filtfilt(b_bp, a_bp, signal_raw)

    # 短波 = 原始 - 長波 - 中波
    shortwave = signal_raw - longwave - midwave

    # 相位計算
    longwave_phase = np.arctan2(np.gradient(longwave), longwave)

    # 寫入數據
    for i, d in enumerate(tension_series):
        d["theoretical_longwave"] = round(float(longwave[i]), 4)
        d["theoretical_midwave"] = round(float(midwave[i]), 4)
        d["theoretical_shortwave"] = round(float(shortwave[i]), 4)
        d["longwave_phase"] = round(float(longwave_phase[i]), 4)
        # 長波趨勢
        if i >= 2:
            trend = longwave[i] - longwave[i - 2]
        else:
            trend = 0
        d["longwave_trend"] = round(float(trend), 4)

    # 偵測 historical peaks
    peak_years = []
    for i in range(2, n - 2):
        if (longwave[i] > longwave[i - 1] and longwave[i] > longwave[i + 1] and
            longwave[i] > np.mean(longwave) + 0.5 * np.std(longwave)):
            peak_years.append(years[i])

    # ── 十年分段統計 ────────────────────────────
    decade_stats = defaultdict(lambda: {"mean_tension": 0, "mean_longwave": 0, "n": 0})
    for d in tension_series:
        dec = (d["year"] // 10) * 10
        decade_stats[dec]["mean_tension"] += d["tension_per_doc"]
        decade_stats[dec]["mean_longwave"] += d["theoretical_longwave"]
        decade_stats[dec]["n"] += 1

    for dec in decade_stats:
        decade_stats[dec]["mean_tension"] /= decade_stats[dec]["n"]
        decade_stats[dec]["mean_longwave"] /= decade_stats[dec]["n"]

    # ── 輸出 ─────────────────────────────────────
    output = {
        "_meta": {
            "version": "0.1.0",
            "built": datetime.now().isoformat(),
            "method": "Keyword composite → Butterworth 4th-order lowpass(0.04)+bandpass[0.04,0.1]",
            "years_analyzed": f"{years[0]}-{years[-1]}",
            "data_points": n,
            "keyword_weights": KEYWORD_WEIGHTS,
            "historical_peaks": peak_years,
            "peak_context": {y: f"https://en.wikipedia.org/wiki/{y}" for y in peak_years},
        },
        "spectrum": tension_series,
        "decade_summary": {
            str(dec): {"mean_tension": round(v["mean_tension"], 4),
                        "mean_longwave": round(v["mean_longwave"], 4)}
            for dec, v in sorted(decade_stats.items())
        },
    }

    os.makedirs(SPECTRUM_OUT.parent, exist_ok=True)
    with open(SPECTRUM_OUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ {SPECTRUM_OUT}")
    print(f"   {n} years ({years[0]}–{years[-1]})")

    # 顯示關鍵趨勢
    print(f"\n  Historical Peaks (longwave crests):")
    for y in peak_years:
        for d in tension_series:
            if d["year"] == y:
                print(f"    {y}: tension={d['tension_per_doc']:.4f}  longwave={d['theoretical_longwave']:.4f}")

    print(f"\n  Decade Averages:")
    for dec in sorted(decade_stats):
        v = decade_stats[dec]
        bar = "█" * int(v["mean_tension"] * 50)
        print(f"    {dec}s: tension={v['mean_tension']:.3f}  longwave={v['mean_longwave']:.3f}  {bar}")

    # 檢測趨勢
    first_half = np.mean([d["theoretical_longwave"] for d in tension_series[:n//2]])
    second_half = np.mean([d["theoretical_longwave"] for d in tension_series[n//2:]])
    print(f"\n  Longwave trajectory: {first_half:.4f} → {second_half:.4f}  (Δ={second_half-first_half:+.4f})")

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()

    result = build()
