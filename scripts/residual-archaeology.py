#!/usr/bin/env python3
"""
residual-archaeology.py — 殘差考古學分析引擎 v1.0

核心問題：
  短波異常年（shortwave outlier years）的文本 crisis type，
  是否可以被當時的長波趨勢解釋？

方法：
  1. 從 theoretical-spectrum.json 讀取短波/長波/中波
  2. 從 DCA results (*.yaml) 提取 crisis_diagnosis.type
  3. 比較：crisis type 與 longwave phase/direction 的對齊程度
  4. 標記「理論突變體」（theoretical mutants）：crisis 與長波脫節的文本

輸出：
  .taskbook/reports/residual-archaeology-{date}.md
"""

import json, os, re, sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

ROOT = Path(__file__).parent.parent
COMPILED = ROOT / "index" / "data" / "compiled-documents.json"
SPECTRUM = ROOT / "index" / "data" / "theoretical-spectrum.json"
DCA_DIR = ROOT / ".taskbook" / "dca-results"
REPORT_DIR = ROOT / ".taskbook" / "reports"

# ── 長波相位 → 預期危機類型映射 ──
# 這是一個假說性的映射表，用於自動標記
# 正值長波相位 (上升) → 預期：capitalist_development / class_formation / organizational_building
# 負值長波相位 (下降) → 預期：economic_crisis / revolutionary_defeat / reaction
# 中立/拐點        → 預期：theoretical_breakthrough / strategic_reassessment

LONGWAVE_CRISIS_EXPECTATION = {
    "rising": [  # longwave_phase > 0.03
        "capitalist_development", "class_formation", "organizational_building",
        "proletarian_growth", "theoretical_advance", "party_consolidation",
        "expansion", "optimism"
    ],
    "falling": [  # longwave_phase < -0.03
        "economic_crisis", "revolutionary_defeat", "reaction",
        "counter_revolution", "repression", "retreat",
        "organizational_degeneration", "theoretical_regression",
        "class_defeat", "pessimism"
    ],
    "neutral": [  # -0.03 <= phase <= 0.03
        "theoretical_breakthrough", "strategic_reassessment",
        "transition", "ambiguity", "reorientation"
    ]
}

def load_db():
    with open(COMPILED) as f:
        return json.load(f)

def load_spectrum():
    with open(SPECTRUM) as f:
        return json.load(f)

def extract_dca_fields(filepath):
    """從 YAML 提取 crisis type, lag layers, direction core"""
    with open(filepath) as f:
        text = f.read()
    
    result = {}
    
    # Crisis type
    m = re.search(r'crisis_diagnosis:\s*\n\s+type:\s*(.+)', text)
    if m:
        result['crisis_type'] = m.group(1).strip()
    
    # Lag layers  
    m = re.search(r'layers:\s*\[(.+?)\]', text)
    if m:
        result['lag_layers'] = [l.strip() for l in m.group(1).split(',')]
    
    # Direction core
    m = re.search(r'direction_constraint:\s*\n\s+core:\s*(.+)', text)
    if m:
        result['direction_core'] = m.group(1).strip()
    
    # Key insight
    m = re.search(r'key_insight:\s*(.+?)(?:\n\s*\n|\n```|\Z)', text, re.DOTALL)
    if m:
        result['key_insight'] = m.group(1).strip()[:200]
    
    return result

def classify_longwave_phase(phase):
    """將長波相位分為 rising / falling / neutral"""
    if phase > 0.03:
        return "rising"
    elif phase < -0.03:
        return "falling"
    else:
        return "neutral"

def crisis_aligned_with_longwave(crisis_type, phase_category):
    """檢查 crisis type 是否與長波相位對齊"""
    if not crisis_type or crisis_type == 'null':
        return None  # 無法判斷
    
    expected = LONGWAVE_CRISIS_EXPECTATION.get(phase_category, [])
    ct_lower = crisis_type.lower()
    
    # 簡單的子串匹配
    for exp in expected:
        if exp in ct_lower or ct_lower in exp:
            return True
    return False

def main():
    today = datetime.now().strftime("%Y%m%d")
    
    db = load_db()
    spec = load_spectrum()
    
    # Build lookup tables
    docs_by_id = {d['id']: d for d in db['documents']}
    
    spectrum_by_year = {}
    for s in spec['spectrum']:
        spectrum_by_year[s['year']] = s
    
    # Load all DCA results
    dca_results = []
    for fname in sorted(os.listdir(DCA_DIR)):
        if not fname.endswith('.yaml'):
            continue
        doc_id = fname.replace('.yaml', '')
        filepath = DCA_DIR / fname
        
        dca = extract_dca_fields(filepath)
        doc = docs_by_id.get(doc_id, {})
        year = doc.get('year')
        
        if year is None:
            continue
        
        spec_entry = spectrum_by_year.get(year, {})
        
        dca_results.append({
            'doc_id': doc_id,
            'title': doc.get('title', '?'),
            'author': doc.get('author', '?'),
            'year': year,
            'crisis_type': dca.get('crisis_type', '?'),
            'lag_layers': dca.get('lag_layers', []),
            'direction_core': dca.get('direction_core', '?'),
            'key_insight': dca.get('key_insight', '?'),
            'shortwave': spec_entry.get('theoretical_shortwave'),
            'longwave': spec_entry.get('theoretical_longwave'),
            'midwave': spec_entry.get('theoretical_midwave'),
            'longwave_phase': spec_entry.get('longwave_phase'),
            'tension_per_doc': spec_entry.get('tension_per_doc'),
            'unreliable': spec_entry.get('_unreliable', False),
        })
    
    # ── Analysis ──
    
    # 1. Top shortwave outliers with DCA
    dca_sorted_sw = sorted(dca_results, key=lambda x: abs(x['shortwave'] or 0), reverse=True)
    
    # 2. Check alignment
    mutants = []
    aligned = []
    uncertain = []
    
    for r in dca_results:
        if r['crisis_type'] in ('?', 'null', None):
            continue
        phase = r['longwave_phase']
        if phase is None:
            continue
        
        phase_cat = classify_longwave_phase(phase)
        is_aligned = crisis_aligned_with_longwave(r['crisis_type'], phase_cat)
        
        entry = {**r, 'phase_category': phase_cat, 'aligned': is_aligned}
        
        if is_aligned is None:
            uncertain.append(entry)
        elif is_aligned:
            aligned.append(entry)
        else:
            mutants.append(entry)
    
    # ── Report ──
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"residual-archaeology-{today}.md"
    
    with open(report_path, 'w') as f:
        f.write(f"# 殘差考古學報告 — Residual Archaeology Report\n\n")
        f.write(f"> 生成日期：{today}\n")
        f.write(f"> DCA 樣本數：{len(dca_results)}\n")
        f.write(f"> 方法：短波異常值 × 長波相位 × crisis type 對齊分析\n\n")
        
        f.write(f"---\n\n")
        f.write(f"## 一、總覽\n\n")
        f.write(f"| 分類 | 數量 | 說明 |\n")
        f.write(f"|------|------|------|\n")
        f.write(f"| 🔴 理論突變體 | **{len(mutants)}** | crisis type 與長波相位脫節 |\n")
        f.write(f"| 🟢 對齊樣本 | {len(aligned)} | crisis type 符合長波預期 |\n")
        f.write(f"| ⚪ 無法判斷 | {len(uncertain)} | crisis type 為 null 或不明確 |\n")
        f.write(f"| **合計** | **{len(dca_results)}** | |\n\n")
        
        # ── Top 20 Shortwave Outliers ──
        f.write(f"---\n\n")
        f.write(f"## 二、短波異常值 Top 20（含 DCA）\n\n")
        f.write(f"| # | Year | Shortwave | Longwave | Phase | Crisis Type | Aligned? |\n")
        f.write(f"|---|------|-----------|----------|-------|-------------|----------|\n")
        for i, r in enumerate(dca_sorted_sw[:20], 1):
            sw = f"{r['shortwave']:+.2f}" if r['shortwave'] else '?'
            lw = f"{r['longwave']:.2f}" if r['longwave'] else '?'
            ph = f"{r['longwave_phase']:+.3f}" if r['longwave_phase'] else '?'
            ct = (r['crisis_type'] or '?')[:40]
            al = '✅' if r.get('aligned') else ('❌' if r.get('aligned') is False else '—')
            f.write(f"| {i} | {r['year']} | {sw} | {lw} | {ph} | {ct} | {al} |\n")
        f.write(f"\n")
        
        # ── Theoretical Mutants ──
        f.write(f"---\n\n")
        f.write(f"## 三、🔴 理論突變體（{len(mutants)} 篇）\n\n")
        f.write(f"這些文本的 crisis type 與其所在年份的長波相位**不一致**——\n")
        f.write(f"它們是短波異常的可能來源，值得深入閱讀。\n\n")
        
        for i, m in enumerate(mutants, 1):
            f.write(f"### {i}. [{m['year']}] {m['doc_id']}: {m['title'][:70]}\n\n")
            f.write(f"- **作者**：{m['author']}\n")
            f.write(f"- **Crisis Type**：`{m['crisis_type']}`\n")
            f.write(f"- **長波相位**：{m['longwave_phase']:+.4f}（{m['phase_category']}）\n")
            f.write(f"- **短波**：{m['shortwave']:+.4f}\n")
            f.write(f"- **長波**：{m['longwave']:.4f}\n")
            f.write(f"- **Lag Layers**：{', '.join(m['lag_layers']) if m['lag_layers'] else '?'}\n")
            f.write(f"- **Direction Core**：{m['direction_core']}\n")
            if m['key_insight'] and m['key_insight'] != '?':
                f.write(f"- **Key Insight**：{m['key_insight'][:150]}\n")
            f.write(f"\n")
        
        # ── Aligned Samples ──
        f.write(f"---\n\n")
        f.write(f"## 四、🟢 對齊樣本（{len(aligned)} 篇，展示前 10）\n\n")
        f.write(f"| Year | ID | Crisis Type | Phase |\n")
        f.write(f"|------|-----|-------------|-------|\n")
        for a in aligned[:10]:
            ct = (a['crisis_type'] or '?')[:35]
            ph = f"{a['longwave_phase']:+.3f}" if a['longwave_phase'] else '?'
            f.write(f"| {a['year']} | {a['doc_id']} | {ct} | {ph} |\n")
        f.write(f"\n")
        
        # ── Crisis Type Distribution ──
        f.write(f"---\n\n")
        f.write(f"## 五、Crisis Type 分佈\n\n")
        ct_counter = Counter(r['crisis_type'] for r in dca_results if r['crisis_type'] not in ('?', 'null', None))
        f.write(f"| Crisis Type | Count |\n")
        f.write(f"|-------------|-------|\n")
        for ct, count in ct_counter.most_common(20):
            f.write(f"| {ct} | {count} |\n")
        f.write(f"\n")
        
        # ── 方法論備註 ──
        f.write(f"---\n\n")
        f.write(f"## 六、方法論備註\n\n")
        f.write(f"- **長波相位分類**：phase > 0.03 = rising, phase < -0.03 = falling, else neutral\n")
        f.write(f"- **對齊判斷**：基於預定義的 `LONGWAVE_CRISIS_EXPECTATION` 映射表（詳見腳本源碼）\n")
        f.write(f"- **限制**：此為自動化初步分類，crisis type 的語義豐富度遠超簡單的子串匹配\n")
        f.write(f"- **建議**：對所有 🔴 標記的理論突變體進行人工閱讀驗證\n\n")
        
        # JSON export for programmatic use
        json_path = REPORT_DIR / f"residual-archaeology-{today}.json"
        with open(json_path, 'w') as jf:
            json.dump({
                'meta': {
                    'date': today,
                    'total_dca': len(dca_results),
                    'mutants': len(mutants),
                    'aligned': len(aligned),
                    'uncertain': len(uncertain),
                },
                'mutants': [{k: v for k, v in m.items() if k != 'aligned'} for m in mutants],
                'aligned': [{k: v for k, v in a.items() if k != 'aligned'} for a in aligned],
            }, jf, indent=2, default=str, ensure_ascii=False)
        f.write(f"JSON export: `{json_path}`\n")
    
    print(f"✅ Report written to: {report_path}")
    print(f"✅ JSON export: {json_path}")
    print(f"\nSummary:")
    print(f"  🔴 Theoretical Mutants: {len(mutants)}")
    print(f"  🟢 Aligned: {len(aligned)}")
    print(f"  ⚪ Uncertain: {len(uncertain)}")
    print(f"  Total DCA analyzed: {len(dca_results)}")

if __name__ == "__main__":
    main()
