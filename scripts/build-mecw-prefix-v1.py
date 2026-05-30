#!/usr/bin/env python3
"""
MECW AI Prefix 生成器 v0.1
為 DeepSeek API 生成固定上下文 Prefix，供語義分析和 DCA 使用。

用法：
  python scripts/build-mecw-prefix.py
  python scripts/build-mecw-prefix.py --stats
"""

import json, os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
COMPILED = ROOT / "index" / "data" / "compiled-documents.json"
NETWORK = ROOT / "index" / "data" / "character-network.json"
PREFIX_OUT = ROOT / "index" / "data" / "mecw-prefix.txt"
STATS_OUT = ROOT / "index" / "data" / "mecw-prefix-stats.json"

def build():
    with open(COMPILED, "r") as f:
        data = json.load(f)
    with open(NETWORK, "r") as f:
        network = json.load(f)

    meta = data["_meta"]
    contacts = network["contacts"]

    lines = []

    # ── 0. 系統標識 ───────────────────────────────
    lines.append("=" * 60)
    lines.append("MECW-index / Second Chamber — Marxist Literature Index")
    lines.append("Two-Chamber Soviet Architecture: ECC (Chamber 1) ∥ MECW (Chamber 2)")
    lines.append("=" * 60)

    # ── 1. 專案定義 ───────────────────────────────
    lines.append("")
    lines.append("## 1. PROJECT DEFINITION")
    lines.append("")
    lines.append("You are analyzing the Marx/Engels Collected Works (MECW),")
    lines.append("the complete English edition in 50 volumes (6,759 documents, 1835-1895).")
    lines.append("")
    lines.append("This corpus includes:")
    lines.append("- 4,306 letters between Marx, Engels, and 694 correspondents")
    lines.append("- 2,211 articles, newspaper commentaries, and theoretical essays")
    lines.append("- 162 chapters from major works (Capital, Anti-Dühring, etc.)")
    lines.append("- 80 prefaces, afterwords, and editorial notes")
    lines.append("")
    lines.append("Source: MARX-ZH-CN/wikirouge-MECW-2026-Jan-ver (CC0 Public Domain)")
    lines.append("")

    # ── 2. 核心理論概念 ───────────────────────────
    lines.append("## 2. CORE THEORETICAL FRAMEWORK")
    lines.append("")
    lines.append("Marx and Engels developed an integrated body of thought. Key concepts:")
    lines.append("")
    lines.append("### Historical Materialism")
    lines.append("- The mode of production conditions social, political, and intellectual life")
    lines.append("- History as the history of class struggles")
    lines.append("- Base (economic structure) and superstructure (state, ideology, culture)")
    lines.append("")
    lines.append("### Critique of Political Economy")
    lines.append("- Commodity fetishism: social relations appear as relations between things")
    lines.append("- Surplus value: the source of capitalist profit extracted from labor")
    lines.append("- Law of the tendency of the rate of profit to fall")
    lines.append("- Primitive accumulation and the genesis of capital")
    lines.append("")
    lines.append("### Class Struggle and Revolution")
    lines.append("- The proletariat as the revolutionary class")
    lines.append("- Dictatorship of the proletariat as transition to classless society")
    lines.append("- The state as instrument of class rule, to wither away under communism")
    lines.append("")
    lines.append("### Dialectics")
    lines.append("- Unity and struggle of opposites")
    lines.append("- Quantitative change → qualitative transformation")
    lines.append("- Negation of the negation")
    lines.append("")

    # ── 3. 歷史時期 ───────────────────────────────
    lines.append("## 3. HISTORICAL PERIODS")
    lines.append("")
    lines.append("1830s: Youth and education. Marx at university, Engels in Bremen.")
    lines.append("1840s: Revolutionary journalism. Rheinische Zeitung, German Ideology,")
    lines.append("       Communist Manifesto (1848). Year of Revolutions.")
    lines.append("1850s: London exile. New York Tribune correspondence. 1857 crisis analysis.")
    lines.append("1860s: Capital Vol.1 (1867). First International (1864-1872).")
    lines.append("1870s: Paris Commune (1871). Critique of the Gotha Programme (1875).")
    lines.append("       Anti-Dühring (1877-78).")
    lines.append("1880s: Marx's death (1883). Engels edits Capital Vol.2-3.")
    lines.append("       Origin of the Family (1884). Second International foundation.")
    lines.append("1890s: Engels' late letters on historical materialism. His death (1895).")
    lines.append("")

    # ── 4. 人物網絡 ───────────────────────────────
    lines.append("## 4. KEY FIGURES")
    lines.append("")
    lines.append("### Primary")
    lines.append("- Karl Marx (1818-1883): philosopher, economist, revolutionary")
    lines.append("- Friedrich Engels (1820-1895): collaborator, patron, editor of Capital Vol.2-3")
    lines.append("")
    lines.append("### Major Correspondents (by letter volume)")
    for i, c in enumerate(contacts[:15], 1):
        m = c.get("letters_from_marx", 0)
        e = c.get("letters_from_engels", 0)
        detail = f"(M:{m} E:{e})" if m or e else ""
        lines.append(f"{i:>2}. {c['name']} — {c['letters_received']} letters {c['first_year']}-{c['last_year']} {detail}")
    lines.append("")

    # ── 5. 關鍵統計 ───────────────────────────────
    lines.append("## 5. CORPUS STATISTICS")
    lines.append(f"- Total documents: {meta['total_documents']}")
    lines.append(f"- Volumes: {meta['volume_count']} (1–50)")
    lines.append(f"- Year range: {meta['year_range'][0]}–{meta['year_range'][1]}")
    lines.append(f"- Peak year: 1848 (319 documents) — Year of Revolutions")
    lines.append(f"- Second peak: 1871 (221 documents) — Paris Commune")
    lines.append("")

    # ── 6. 文獻類型 ───────────────────────────────
    lines.append("## 6. DOCUMENT TYPES")
    lines.append("- letter: Personal correspondence, often revealing theoretical development in real-time")
    lines.append("- article: Published journalism and theoretical essays")
    lines.append("- chapter: Extracted chapters from major works")
    lines.append("- paratext: Prefaces, afterwords, editorial introductions")
    lines.append("")

    # ── 7. DCA 分析框架 ─────────────────────────────
    lines.append("## 7. DCA ANALYSIS FRAMEWORK")
    lines.append("")
    lines.append("For each document, apply the DCA (Crisis-Delay-Alternative-Direction) method:")
    lines.append("")
    lines.append("**Crisis** — What specific historical crisis does this text respond to?")
    lines.append("  (e.g., 1848 revolution defeat, 1857 economic crisis, 1871 Commune suppression)")
    lines.append("")
    lines.append("**Delay (Lag)** — What structural lag does the text diagnose?")
    lines.append("  (e.g., proletariat not yet organized, theory lagging behind practice,")
    lines.append("   bourgeois ideology blocking class consciousness)")
    lines.append("")
    lines.append("**Alternative** — What alternative path or solution does the text propose?")
    lines.append("  (e.g., workers' party, dictatorship of proletariat, cooperative production)")
    lines.append("")
    lines.append("**Direction** — What material constraints shape the direction proposed?")
    lines.append("  (e.g., level of productive forces, existing class composition, geopolitical situation)")
    lines.append("")

    # ── 8. 輸出格式 ───────────────────────────────
    lines.append("## 8. OUTPUT FORMAT")
    lines.append("")
    lines.append("Return analysis in YAML-compatible structured format:")
    lines.append("```yaml")
    lines.append("document_id: MECW01-004")
    lines.append("theoretical_position: critique  # critique|defense|synthesis|polemic|analysis")
    lines.append("crisis_diagnosis: \"...\"")
    lines.append("lag_mechanism: \"...\"")
    lines.append("alternative_proposal: \"...\"")
    lines.append("direction_constraint: \"...\"")
    lines.append("confidence: 0.85")
    lines.append("key_concepts: [surplus_value, exploitation, labour_power]")
    lines.append("```")
    lines.append("")

    prefix = "\n".join(lines)

    # Write
    os.makedirs(PREFIX_OUT.parent, exist_ok=True)
    with open(PREFIX_OUT, "w", encoding="utf-8") as f:
        f.write(prefix)

    # Stats
    tokens_est = len(prefix.split())  # rough estimate
    stats = {
        "built": datetime.now().isoformat(),
        "characters": len(prefix),
        "words": len(prefix.split()),
        "lines": len(lines),
        "estimated_tokens": tokens_est,
        "file": str(PREFIX_OUT),
    }
    with open(STATS_OUT, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    return stats


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()

    stats = build()
    if args.stats:
        for k, v in stats.items():
            print(f"  {k}: {v}")
    else:
        print(f"✅ MECW Prefix → {PREFIX_OUT}")
        print(f"   {stats['words']} words, ~{stats['estimated_tokens']} tokens")
        print(f"   Stats → {STATS_OUT}")
