#!/usr/bin/env python3
"""
build-stratified-dca-sample.py — 分層抽樣 DCA 提取隊列生成器

策略：
  L1  短波極值年    Top-5 shortwave 異常年，每 3 篇 Marx article  = ~15
  L2  長波相位錨點  波峰(1848,1871) + 波谷(1857,1878) × 每 3 篇   = ~12
  L3  十年校準      1840s/50s/60s/70s/80s 每十年 5 篇 Marx article = ~25
  L4  隨機對照      全庫隨機 30 篇 article（任何作者）              = ~30
  L5  危機類型補充  預留（後續根據已提取結果補足）                  = ~18
  ─────────────────────────────────────────────────────────────
  合計                                                          ≈ 100

輸出：.taskbook/dca-sample-queue.txt（一行一個 doc ID）
"""

import json, random, sys
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).parent.parent
COMPILED = ROOT / "index" / "data" / "compiled-documents.json"
SPECTRUM = ROOT / "index" / "data" / "theoretical-spectrum.json"
OUT_DIR = ROOT / ".taskbook" / "dca-results"
QUEUE_FILE = ROOT / ".taskbook" / "dca-sample-queue.txt"

def load_db():
    with open(COMPILED) as f:
        return json.load(f)

def load_spectrum():
    with open(SPECTRUM) as f:
        return json.load(f)

def already_done(doc_id):
    return (OUT_DIR / f"{doc_id}.yaml").exists()

def get_docs_by_year(db):
    by_year = defaultdict(list)
    for d in db["documents"]:
        y = d.get("year")
        if y is not None and d.get("doc_type") in ("article", "chapter"):
            by_year[y].append(d)
    return by_year

def pick_marx_articles(docs, n, seed=42):
    """從文檔列表中優先選 Marx 文章，不夠則補 Engels"""
    rng = random.Random(seed)
    marx = [d for d in docs if 'Marx' in str(d.get('author', ''))]
    engels = [d for d in docs if 'Engels' in str(d.get('author', '')) and d not in marx]
    others = [d for d in docs if d not in marx and d not in engels]
    
    selected = []
    # First from Marx
    pool = marx.copy()
    rng.shuffle(pool)
    for d in pool:
        if len(selected) >= n:
            break
        if not already_done(d['id']):
            selected.append(d['id'])
    
    # Then from Engels
    if len(selected) < n:
        pool = engels.copy()
        rng.shuffle(pool)
        for d in pool:
            if len(selected) >= n:
                break
            if not already_done(d['id']) and d['id'] not in selected:
                selected.append(d['id'])
    
    # Then others
    if len(selected) < n:
        pool = others.copy()
        rng.shuffle(pool)
        for d in pool:
            if len(selected) >= n:
                break
            if not already_done(d['id']) and d['id'] not in selected:
                selected.append(d['id'])
    
    return selected

def main():
    db = load_db()
    spec = load_spectrum()
    by_year = get_docs_by_year(db)
    
    all_ids = set()
    plan = {}
    
    # ── L1: 短波極值年 (Top 5) ──
    reliable = [s for s in spec['spectrum'] if not s.get('_unreliable', False)]
    reliable_sorted = sorted(reliable, key=lambda x: abs(x['theoretical_shortwave']), reverse=True)
    top5_years = [r['year'] for r in reliable_sorted[:5]]
    
    l1_ids = []
    for year in top5_years:
        docs = by_year.get(year, [])
        picked = pick_marx_articles(docs, 3, seed=year)
        l1_ids.extend(picked)
        print(f"L1 {year} (shortwave={next(r['theoretical_shortwave'] for r in reliable_sorted if r['year']==year):+.2f}): {len(picked)} docs")
    
    plan['L1_shortwave_outliers'] = {'years': top5_years, 'ids': l1_ids, 'n': len(l1_ids)}
    all_ids.update(l1_ids)
    
    # ── L2: 長波相位錨點 ──
    # Find peaks and troughs in longwave
    longwave_vals = [(s['year'], s['theoretical_longwave']) for s in reliable]
    
    # Peaks (approximate): 1848, 1877
    # Troughs (approximate): 1857, 1886
    phase_years = {
        'peak_1848': 1848,
        'trough_1857': 1857,
        'peak_1871': 1871,
        'trough_1878': 1878,  # or 1886
    }
    
    l2_ids = []
    for label, year in phase_years.items():
        docs = by_year.get(year, [])
        picked = pick_marx_articles(docs, 3, seed=hash(label))
        l2_ids.extend(picked)
        lw_val = next((s['theoretical_longwave'] for s in reliable if s['year']==year), '?')
        print(f"L2 {label} ({year}, longwave={lw_val}): {len(picked)} docs")
    
    plan['L2_longwave_anchors'] = {'years': list(phase_years.values()), 'ids': l2_ids, 'n': len(l2_ids)}
    all_ids.update(l2_ids)
    
    # ── L3: 十年校準 ──
    decades = {
        '1840s': (1842, 1849),
        '1850s': (1850, 1859),
        '1860s': (1860, 1869),
        '1870s': (1870, 1879),
        '1880s': (1880, 1889),
    }
    
    l3_ids = []
    for label, (start, end) in decades.items():
        decade_docs = []
        for y in range(start, end+1):
            decade_docs.extend(by_year.get(y, []))
        picked = pick_marx_articles(decade_docs, 5, seed=hash(label))
        l3_ids.extend(picked)
        print(f"L3 {label} ({start}-{end}): {len(picked)} docs from {len(decade_docs)} available")
    
    plan['L3_decadal'] = {'decades': list(decades.keys()), 'ids': l3_ids, 'n': len(l3_ids)}
    all_ids.update(l3_ids)
    
    # ── L4: 隨機對照 ──
    rng = random.Random(42)
    all_articles = [d for d in db["documents"] 
                    if d.get("doc_type") in ("article", "chapter")
                    and d["id"] not in all_ids
                    and not already_done(d["id"])]
    rng.shuffle(all_articles)
    l4_ids = [d['id'] for d in all_articles[:30]]
    plan['L4_random_control'] = {'ids': l4_ids, 'n': len(l4_ids)}
    all_ids.update(l4_ids)
    print(f"L4 random control: {len(l4_ids)} docs")
    
    # ── Summary ──
    print(f"\n{'='*50}")
    print(f"Total unique IDs: {len(all_ids)}")
    print(f"  L1 shortwave: {plan['L1_shortwave_outliers']['n']}")
    print(f"  L2 longwave:  {plan['L2_longwave_anchors']['n']}")
    print(f"  L3 decadal:   {plan['L3_decadal']['n']}")
    print(f"  L4 random:    {plan['L4_random_control']['n']}")
    
    # Estimate cost
    est_tokens_per = 7000
    est_cost_per = 0.0036
    total_est_cost = len(all_ids) * est_cost_per
    print(f"\nEstimated: {len(all_ids)} × {est_tokens_per} tokens ≈ ${total_est_cost:.2f}")
    
    # Write queue
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_FILE, 'w') as f:
        for doc_id in sorted(all_ids):
            f.write(doc_id + '\n')
    print(f"\nQueue written to: {QUEUE_FILE}")
    
    # Also save plan
    plan_path = ROOT / ".taskbook" / "dca-sample-plan.json"
    with open(plan_path, 'w') as f:
        json.dump(plan, f, indent=2, default=str)
    print(f"Plan written to: {plan_path}")

if __name__ == "__main__":
    main()
