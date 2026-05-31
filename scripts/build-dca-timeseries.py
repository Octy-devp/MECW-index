#!/usr/bin/env python3
"""
DCA 結構時間序列化器 v0.1
從 20 篇 DCA 結果 + 手動報告中提取結構化時間序列：
  - crisis_type 年頻率
  - lag_mechanism 層級追蹤
  - alternative_proposal 關鍵概念追蹤
  - 與 keyword tension 做交叉頻譜

用法：
  python scripts/build-dca-timeseries.py
"""

import json, os, re, yaml
from pathlib import Path
from collections import defaultdict
from datetime import datetime

ROOT = Path(__file__).parent.parent
DCA_RESULTS = ROOT / ".taskbook" / "dca-results"
SPECTRUM_IN = ROOT / "index" / "data" / "theoretical-spectrum.json"
OUT = ROOT / "index" / "data" / "dca-structure-timeseries.json"

# ── DCA 結構標籤提取規則 ──────────────────────────

CRISIS_PATTERNS = {
    "revolutionary_conjuncture": [r"revolutionary.conjuncture", r"1848", r"revolutionary.upheaval"],
    "organizational_degeneration": [r"organizational.degeneration", r"principled.retreat", r"theoretical.retreat"],
    "ideological_offensive": [r"ideological.offensive", r"bourgeois.press", r"slander"],
    "methodological_crisis": [r"methodological", r"category.error", r"commodity.fetishism"],
    "geopolitical_trajectory": [r"geopolitical", r"tsardom", r"world.war"],
    "technological_rupture": [r"technological", r"ironclad", r"military"],
    "knowledge_asymmetry": [r"knowledge.asymmetry", r"workers.inquiry", r"counter.apparatus"],
    "theoretical_disarmament": [r"theoretical.disarmament", r"utopian", r"scientific.socialism"],
    "qualitative_transformation": [r"qualitative.transformation", r"may.day", r"international.army"],
}

LAG_PATTERNS = {
    "organizational": [r"organizational", r"organization", r"party.formation", r"workers.organized"],
    "ideological": [r"ideological", r"bourgeois.ideology", r"consciousness", r"servile.belief"],
    "theoretical": [r"theoretical", r"lassalle.did.not.know", r"scientific.understanding"],
    "class_fragmentation": [r"class.fragmentation", r"peasantry", r"parcelized"],
    "institutional_inertia": [r"institutional.inertia", r"admiralty", r"fixed.capital"],
    "intellectual_tradition": [r"intellectual.tradition", r"german.philosophy", r"hegel"],
    "historical_memory": [r"historical.memory", r"chartist", r"1848.defeat"],
    "epistemological": [r"epistemological", r"knowledge", r"inquiry"],
}

ALT_PATTERNS = {
    "dictatorship_of_proletariat": [r"dictatorship.of.the.proletariat", r"revolutionary.dictatorship"],
    "smash_state_machine": [r"smash.the.state", r"smash.*machine"],
    "workers_party": [r"workers.party", r"political.party", r"party.formation"],
    "internationalism": [r"international", r"internationalism"],
    "scientific_socialism": [r"scientific.socialism", r"materialist.conception"],
    "cooperative_production": [r"cooperative", r"co-operative"],
    "withering_away": [r"wither.away", r"administration.of.things"],
    "two_phase_communism": [r"two.phase", r"phase.*communis", r"from.each.according"],
}

def extract_patterns(text, patterns):
    """從文本中匹配模式，回傳匹配到的標籤"""
    matches = []
    for label, regexes in patterns.items():
        for regex in regexes:
            if re.search(regex, text, re.IGNORECASE):
                matches.append(label)
                break
    return matches

def parse_dca_file(filepath):
    """解析一個 DCA YAML 檔案"""
    with open(filepath) as f:
        content = f.read()
    # Remove code block wrapper
    content = re.sub(r'^```yaml?\n?', '', content)
    content = re.sub(r'\n?```$', '', content)
    try:
        return yaml.safe_load(content)
    except:
        return None

def build():
    # ── 載入 DCA 結果 ──────────────────────────
    dca_data = []
    if DCA_RESULTS.exists():
        for f in sorted(os.listdir(DCA_RESULTS)):
            if not f.endswith('.yaml'):
                continue
            doc_id = f.replace('.yaml', '')
            dca = parse_dca_file(DCA_RESULTS / f)
            if not dca:
                print(f"  ⚠️ {f}: parse failed")
                continue

            # 提取年份（從 compiled DB）
            year = None
            # Try to parse from filename or content
            year_match = re.search(r'MECW(\d+)', doc_id)
            volume = int(year_match.group(1)) if year_match else 0

            dca_data.append({
                "id": doc_id,
                "volume": volume,
                "year": None,  # will be filled from compiled DB
                "crisis_types": extract_patterns(
                    str(dca.get("crisis_diagnosis", "")), CRISIS_PATTERNS),
                "lag_layers": extract_patterns(
                    str(dca.get("lag_mechanism", "")), LAG_PATTERNS),
                "alt_concepts": extract_patterns(
                    str(dca.get("alternative_proposal", "")), ALT_PATTERNS),
                "has_reasoning": "reasoning" in (dca or {}),
                "dca_completeness": dca.get("dca_completeness", "unknown") if dca else "unknown",
            })

    print(f"Parsed {len(dca_data)} DCA results")

    # ── 從 compiled DB 補年份 ──────────────────
    with open(ROOT / "index/data/compiled-documents.json") as f:
        db = json.load(f)

    doc_map = {d["id"]: d for d in db["documents"]}
    for item in dca_data:
        doc = doc_map.get(item["id"])
        if doc:
            item["year"] = doc.get("year")
            item["title"] = doc.get("title", "")[:60]

    # ── 時間序列化 ────────────────────────────
    years = sorted(set(item["year"] for item in dca_data
                       if item["year"] and isinstance(item["year"], int)))

    # Crisis type 年頻率
    crisis_ts = defaultdict(lambda: defaultdict(int))
    lag_ts = defaultdict(lambda: defaultdict(int))
    alt_ts = defaultdict(lambda: defaultdict(int))

    for item in dca_data:
        y = item.get("year")
        if not y or not isinstance(y, int):
            continue
        for ct in item["crisis_types"]:
            crisis_ts[ct][y] += 1
        for ll in item["lag_layers"]:
            lag_ts[ll][y] += 1
        for ac in item["alt_concepts"]:
            alt_ts[ac][y] += 1

    # ── 交叉頻譜（與 keyword tension 比對）─────
    with open(SPECTRUM_IN) as f:
        spectrum = json.load(f)

    tension_by_year = {d["year"]: d.get("theoretical_longwave", 0)
                       for d in spectrum["spectrum"]}

    # 計算危機類型密度與 longwave 的相關性
    correlations = {}
    for ct in crisis_ts:
        vals_crisis = []
        vals_longwave = []
        for y in years:
            vals_crisis.append(crisis_ts[ct].get(y, 0))
            vals_longwave.append(tension_by_year.get(y, 0))
        if len(vals_crisis) > 3:
            corr = np.corrcoef(vals_crisis, vals_longwave)[0, 1] if any(vals_crisis) else 0
            correlations[ct] = round(float(corr), 3)

    # ── 輸出 ──────────────────────────────────
    output = {
        "_meta": {
            "version": "0.1.0",
            "built": datetime.now().isoformat(),
            "dca_results_parsed": len(dca_data),
            "years_covered": f"{min(years)}-{max(years)}" if years else "N/A",
        },
        "dca_entries": dca_data,
        "crisis_type_timeseries": {
            ct: [{"year": y, "count": crisis_ts[ct].get(y, 0)}
                 for y in sorted(set(list(crisis_ts[ct].keys()) + years))]
            for ct in sorted(crisis_ts)
        },
        "lag_layer_timeseries": {
            ll: [{"year": y, "count": lag_ts[ll].get(y, 0)}
                 for y in sorted(set(list(lag_ts[ll].keys()) + years))]
            for ll in sorted(lag_ts)
        },
        "alternative_concept_timeseries": {
            ac: [{"year": y, "count": alt_ts[ac].get(y, 0)}
                 for y in sorted(set(list(alt_ts[ac].keys()) + years))]
            for ac in sorted(alt_ts)
        },
        "cross_spectrum_correlations": correlations,
        "insights": generate_insights(crisis_ts, lag_ts, alt_ts, correlations, tension_by_year),
    }

    os.makedirs(OUT.parent, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ {OUT}")
    print(f"   {len(dca_data)} entries, {len(years)} years")

    # 報告
    print(f"\n  Crisis Type × Longwave Correlations:")
    for ct, corr in sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True):
        sig = "***" if abs(corr) > 0.7 else ("**" if abs(corr) > 0.5 else ("*" if abs(corr) > 0.3 else ""))
        print(f"    {ct}: r={corr:+.3f} {sig}")

    print(f"\n  Lag Layer Distribution:")
    for ll in sorted(lag_ts):
        total = sum(lag_ts[ll].values())
        print(f"    {ll}: {total} occurrences")

    print(f"\n  Alternative Concepts Over Time:")
    for ac in sorted(alt_ts):
        years_present = sorted(lag_ts.get(ac, {}).keys()) if ac in lag_ts else []
        first = min(alt_ts[ac].keys()) if alt_ts[ac] else "?"
        last = max(alt_ts[ac].keys()) if alt_ts[ac] else "?"
        total = sum(alt_ts[ac].values())
        print(f"    {ac}: {total}× ({first}–{last})")

    return output

def generate_insights(crisis_ts, lag_ts, alt_ts, correlations, tension_by_year):
    """自動生成分析洞察"""
    insights = []

    # 哪種危機與長波最相關？
    if correlations:
        top = max(correlations, key=lambda k: abs(correlations[k]))
        insights.append(f"'{top}' crisis type shows strongest correlation with longwave tension (r={correlations[top]:.3f})")

    # 哪種滯後最常見？
    if lag_ts:
        top_lag = max(lag_ts, key=lambda k: sum(lag_ts[k].values()))
        insights.append(f"'{top_lag}' is the most frequent lag mechanism ({sum(lag_ts[top_lag].values())} occurrences)")

    # 替代概念的歷史演變
    if alt_ts:
        for ac in ["dictatorship_of_proletariat", "scientific_socialism", "workers_party"]:
            if ac in alt_ts and alt_ts[ac]:
                years = sorted(alt_ts[ac].keys())
                insights.append(f"'{ac}': first appears {min(years)}, peaks in {max(alt_ts[ac], key=alt_ts[ac].get)}")

    return insights


if __name__ == "__main__":
    import numpy as np
    build()
