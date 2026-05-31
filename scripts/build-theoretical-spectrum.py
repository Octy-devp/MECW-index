#!/usr/bin/env python3
"""
MECW 理論張力頻譜計算器 v0.2 — 校準版
v0.1 → v0.2 校準：
  - 小樣本年份加權（文獻數 < 50 → tension × 衰減因數）
  - Butterworth order: 4→2（減少過度平滑）
  - Peak detection: scipy.signal.find_peaks（更敏感）
  - 新增 decade keyword contribution（哪些詞驅動張力）
  - 新增 per-keyword 長波分解（供 ANOVA 校準）

用法：
  python scripts/build-theoretical-spectrum.py
  /workspaces/ECC/.venv/bin/python3 scripts/build-theoretical-spectrum.py
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

# Butterworth 參數（v0.2 調整）
LOWPASS_CUTOFF = 0.05   # 0.04→0.05：讓 1848 年的信號通過
BANDPASS_LOW = 0.04
BANDPASS_HIGH = 0.12
FILTER_ORDER = 2         # 4→2：減少過度平滑，保留更多變異

# 小樣本閾值
MIN_DOCS_THRESHOLD = 50  # 年份文獻 < 50 → 衰減

# 關鍵詞權重（初步，後續 ANOVA 校準）
KEYWORD_WEIGHTS = {
    "revolution": 1.5,
    "class": 1.3,
    "proletariat": 1.2,
    "capital": 1.1,
    "communism": 1.4,
    "state": 0.9,
    "labour": 0.8,
    "party": 1.0,
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
    kw_contributions = {kw: defaultdict(float) for kw in KEYWORD_WEIGHTS}
    for year in years:
        composite = 0.0
        for kw, weight in KEYWORD_WEIGHTS.items():
            kw_series = {d["year"]: d["freq_per_10k"] for d in kw_data.get(kw, [])}
            freq = kw_series.get(year, 0)
            composite += freq * weight
            kw_contributions[kw][year] = round(freq, 2)
        n_docs = docs_per_year.get(year, 1)
        # v0.2: 小樣本衰減
        decay = min(1.0, n_docs / MIN_DOCS_THRESHOLD)
        tension_series.append({
            "year": year,
            "tension_raw": round(composite, 2),
            "tension_per_doc": round(composite / max(n_docs, 1) * decay, 4),
            "documents": n_docs,
            "_unreliable": decay < 1.0,
            "_sample_decay": round(decay, 3),
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

    # 偵測 historical peaks (v0.2: scipy.find_peaks)
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(longwave, prominence=0.03 * np.std(longwave), distance=3)
    peak_years = [tension_series[p]["year"] for p in peaks]

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

    # ── v0.2 Decade keyword contributions ──
    decade_kw = defaultdict(lambda: defaultdict(float))
    decade_kw_n = defaultdict(int)
    for d in tension_series:
        dec = (d["year"] // 10) * 10
        for kw in KEYWORD_WEIGHTS:
            decade_kw[dec][kw] += kw_contributions[kw].get(d["year"], 0)
        decade_kw_n[dec] += 1

    # ── 輸出 ─────────────────────────────────────
    output = {
        "_meta": {
            "version": "0.2.0",
            "changelog": "v0.1→v0.2: 小樣本衰減 + order 4→2 + cutoff 0.04→0.05 + scipy.find_peaks + kw contributions",
            "built": datetime.now().isoformat(),
            "method": f"Butterworth {FILTER_ORDER}nd-order lowpass({LOWPASS_CUTOFF})+bandpass[{BANDPASS_LOW},{BANDPASS_HIGH}]",
            "years_analyzed": f"{years[0]}-{years[-1]}",
            "data_points": n,
            "keyword_weights": KEYWORD_WEIGHTS,
            "historical_peaks": peak_years,
            "small_sample_threshold": MIN_DOCS_THRESHOLD,
            "unreliable_years": [d["year"] for d in tension_series if d["_unreliable"]],
        },
        "spectrum": tension_series,
        "decade_keyword_contributions": {
            str(dec): {kw: round(v / max(decade_kw_n[dec], 1), 2)
                       for kw, v in sorted(kws.items(), key=lambda x: x[1], reverse=True)}
            for dec, kws in sorted(decade_kw.items())
        },
    }

    os.makedirs(SPECTRUM_OUT.parent, exist_ok=True)
    with open(SPECTRUM_OUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ {SPECTRUM_OUT} (v0.2)")
    print(f"   {n} years ({years[0]}–{years[-1]})")
    print(f"   Unreliable: {len(output['_meta']['unreliable_years'])} years (<{MIN_DOCS_THRESHOLD} docs)")

    print(f"\n  Historical Peaks (longwave crests):")
    for y in peak_years:
        for d in tension_series:
            if d["year"] == y:
                tag = " ⚠️" if d["_unreliable"] else ""
                print(f"    {y}: tension={d['tension_per_doc']:.4f}  longwave={d['theoretical_longwave']:.4f}{tag}")

    print(f"\n  Decade Tension + Top 3 Keywords:")
    for dec in sorted(decade_kw):
        kws = decade_kw[dec]
        top3 = sorted(kws.items(), key=lambda x: x[1], reverse=True)[:3]
        avg_t = sum(d["tension_per_doc"] for d in tension_series
                     if (d["year"]//10)*10 == dec) / max(decade_kw_n[dec], 1)
        bar = "█" * int(avg_t * 40)
        kw_str = ", ".join(f"{k}({v/decade_kw_n[dec]:.1f})" for k, v in top3)
        print(f"    {dec}s: t={avg_t:.3f} {bar}  [{kw_str}]")

    # 長波軌跡
    first_half = np.mean([d["theoretical_longwave"] for d in tension_series[:n//2]])
    second_half = np.mean([d["theoretical_longwave"] for d in tension_series[n//2:]])
    print(f"\n  Longwave: {first_half:.4f} → {second_half:.4f}  (Δ={second_half-first_half:+.4f})")
    print(f"  v0.2 changes: sample_decay, order 4→2, cutoff 0.04→0.05, scipy peaks")

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()

    result = build()
