#!/usr/bin/env python3
"""
MECW 批量分析器 v0.1
一次性完成所有純本地分析任務：
  1. 人物檔案生成（Top 50 → index/characters/）
  2. 關鍵詞時間追蹤（5 核心詞彙 × 60 年）
  3. 十年摘要（1840s–1890s）
  4. 地點提取（從書信內文）

用法：
  python scripts/bulk-analyze.py
"""

import json, os, re, argparse
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

ROOT = Path(__file__).parent.parent
COMPILED = ROOT / "index" / "data" / "compiled-documents.json"
NETWORK = ROOT / "index" / "data" / "character-network.json"
CHARACTERS_DIR = ROOT / "index" / "characters"
KEYWORDS_OUT = ROOT / "index" / "data" / "keyword-timeseries.json"
DECADE_OUT = ROOT / "index" / "data" / "decade-summary.md"
LOCATIONS_OUT = ROOT / "index" / "data" / "location-stats.json"

# ── 關鍵詞（正則，大小寫不敏感）──────────────────────
KEYWORDS = {
    "revolution": re.compile(r'\brevolution[sa-z]*\b', re.IGNORECASE),
    "capital": re.compile(r'\bcapital[sa-z]*\b', re.IGNORECASE),
    "proletariat": re.compile(r'\bproletari[aeo][a-z]*\b', re.IGNORECASE),
    "state": re.compile(r'\bstate[s]?\b', re.IGNORECASE),
    "communism": re.compile(r'\bcommunis[mt][a-z]*\b', re.IGNORECASE),
    "class": re.compile(r'\bclass[ea]?[s]?\b', re.IGNORECASE),
    "labour": re.compile(r'\blabou?r[ea]?[rs]?\b', re.IGNORECASE),
    "party": re.compile(r'\bpart(?:y|ies)\b', re.IGNORECASE),
}

# ── 已知寫作地點 ─────────────────────────────────────
KNOWN_LOCATIONS = {
    "London": ["London", "Londres"],
    "Manchester": ["Manchester"],
    "Paris": ["Paris"],
    "Brussels": ["Brussels", "Bruxelles", "Brüssel"],
    "Berlin": ["Berlin"],
    "Cologne": ["Cologne", "Köln", "Cöln"],
    "Vienna": ["Vienna", "Wien"],
    "New York": ["New York"],
    "Geneva": ["Geneva", "Genève", "Genf"],
    "Zurich": ["Zurich", "Zürich"],
    "Hamburg": ["Hamburg"],
    "Trier": ["Trier"],
    "Barmen": ["Barmen"],
    "Bremen": ["Bremen"],
    "Frankfurt": ["Frankfurt"],
    "Leipzig": ["Leipzig"],
}


def analyze():
    with open(COMPILED, "r") as f:
        data = json.load(f)
    with open(NETWORK, "r") as f:
        network = json.load(f)

    documents = data["documents"]
    contacts = {c["name"]: c for c in network["contacts"]}
    print(f"Loaded {len(documents)} documents, {len(contacts)} contacts")

    # ── 初始化追蹤器 ──────────────────────────────
    keyword_by_year = {kw: defaultdict(int) for kw in KEYWORDS}
    location_counts = Counter()
    decade_docs = defaultdict(list)
    total_words_by_year = defaultdict(int)

    # ── 第一遍：掃描所有文獻 ──────────────────────
    for i, doc in enumerate(documents):
        year = doc.get("year")
        if not year or not isinstance(year, int):
            continue
        if year < 1835 or year > 1895:
            continue

        # 十年分類
        decade = (year // 10) * 10
        decade_docs[decade].append(doc)

        # 讀取全文
        filepath = doc.get("_filepath")
        if not filepath:
            continue
        full_path = ROOT / filepath
        if not full_path.exists():
            continue

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except:
            continue

        # 分離 body（跳過 frontmatter）
        parts = content.split("---", 2)
        body = parts[2] if len(parts) > 2 else content

        # 關鍵詞計數
        words = len(body.split())
        total_words_by_year[year] += words
        for kw, pattern in KEYWORDS.items():
            count = len(pattern.findall(body))
            keyword_by_year[kw][year] += count

        # 地點提取（從前 200 字符 + 後 200 字符）
        head = body[:300]
        tail = body[-300:] if len(body) > 300 else ""
        search_zone = head + " " + tail
        for canon, aliases in KNOWN_LOCATIONS.items():
            for alias in aliases:
                if alias in search_zone:
                    location_counts[canon] += 1
                    break

        if (i + 1) % 2000 == 0:
            print(f"  Scanned {i+1}/{len(documents)}...")

    # ── 輸出 1：關鍵詞時間序列 ───────────────────
    keyword_data = {}
    for kw in KEYWORDS:
        series = []
        for year in sorted(keyword_by_year[kw]):
            total_words = total_words_by_year.get(year, 1)
            freq = keyword_by_year[kw][year] / max(total_words, 1) * 10000  # per 10k words
            series.append({"year": year, "count": keyword_by_year[kw][year], "freq_per_10k": round(freq, 2)})
        keyword_data[kw] = series

    keyword_output = {
        "_meta": {
            "version": "0.1.0",
            "built": datetime.now().isoformat(),
            "keywords": list(KEYWORDS.keys()),
            "total_words_analyzed": sum(total_words_by_year.values()),
        },
        "keywords": keyword_data,
    }

    os.makedirs(KEYWORDS_OUT.parent, exist_ok=True)
    with open(KEYWORDS_OUT, "w", encoding="utf-8") as f:
        json.dump(keyword_output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Keywords → {KEYWORDS_OUT}")

    # ── 輸出 2：地點統計 ─────────────────────────
    location_output = {
        "_meta": {"built": datetime.now().isoformat()},
        "locations": [{"name": k, "count": v} for k, v in location_counts.most_common()],
    }
    with open(LOCATIONS_OUT, "w", encoding="utf-8") as f:
        json.dump(location_output, f, ensure_ascii=False, indent=2)
    print(f"✅ Locations → {LOCATIONS_OUT} ({len(location_counts)} places)")

    # ── 輸出 3：十年摘要 ─────────────────────────
    decade_lines = [
        "# MECW 十年摘要",
        f"\n> 自動生成：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 核心時期：1835–1895\n",
    ]

    for dec in sorted(decade_docs):
        docs = decade_docs[dec]
        letters = sum(1 for d in docs if d.get("doc_type") == "letter")
        articles = sum(1 for d in docs if d.get("doc_type") == "article")
        chapters = sum(1 for d in docs if d.get("doc_type") == "chapter")

        # Top authors this decade
        author_counts = Counter()
        for d in docs:
            a = d.get("author", "")
            if "Marx" in a and "Engels" not in a:
                author_counts["Karl Marx"] += 1
            elif "Engels" in a and "Marx" not in a:
                author_counts["Friedrich Engels"] += 1
            elif "Marx" in a and "Engels" in a:
                author_counts["Marx & Engels"] += 1
            else:
                author_counts[a] += 1

        # Top keywords this decade
        kw_decade = {}
        for kw in KEYWORDS:
            total = sum(keyword_by_year[kw].get(y, 0) for y in range(dec, dec + 10))
            words = sum(total_words_by_year.get(y, 1) for y in range(dec, dec + 10))
            kw_decade[kw] = round(total / max(words, 1) * 10000, 1)

        decade_lines.append(f"## {dec}s（{len(docs)} 篇文獻）\n")
        decade_lines.append(f"| 類型 | 數量 |")
        decade_lines.append(f"|------|:---:|")
        decade_lines.append(f"| Letters | {letters} |")
        decade_lines.append(f"| Articles | {articles} |")
        decade_lines.append(f"| Chapters | {chapters} |")
        decade_lines.append("")

        decade_lines.append(f"**主要作者**：{', '.join(f'{a}({c})' for a,c in author_counts.most_common(5))}\n")
        decade_lines.append(f"**關鍵詞頻率（per 10k words）**：")
        for kw, fq in sorted(kw_decade.items(), key=lambda x: x[1], reverse=True):
            decade_lines.append(f"  - {kw}: {fq}")
        decade_lines.append("")

        # 代表性文獻
        decade_lines.append(f"**代表性文獻**：")
        sample = [d for d in docs if d.get("doc_type") != "paratext"][:8]
        for d in sample:
            y = d.get("year", "?")
            title = d.get("title", "")[:100]
            decade_lines.append(f"  - [{y}] {title}")
        decade_lines.append("")

    with open(DECADE_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(decade_lines))
    print(f"✅ Decade summary → {DECADE_OUT}")

    # ── 輸出 4：人物檔案 ─────────────────────────
    os.makedirs(CHARACTERS_DIR, exist_ok=True)
    top_contacts = network["contacts"][:50]
    created = 0

    for contact in top_contacts:
        name = contact["name"]
        safe_name = re.sub(r'[^a-zA-Z]', '-', name.lower()).strip('-')[:60]
        if not safe_name:
            safe_name = "unnamed"

        lines = [
            f"# {name}",
            f"\n> MECW 通信對象 · 自動生成",
            "",
            f"| 屬性 | 值 |",
            f"|------|-----|",
            f"| 收到信件 | {contact['letters_received']} |",
            f"| 來自 Marx | {contact['letters_from_marx']} |",
            f"| 來自 Engels | {contact['letters_from_engels']} |",
            f"| 時期 | {contact['first_year']}–{contact['last_year']} |",
            "",
            "## 通信記錄",
            "",
        ]

        # 列出所有信件
        docs_map = {d["id"]: d for d in documents}
        for lid in contact["letter_ids"]:
            d = docs_map.get(lid)
            if d:
                y = d.get("year", "?")
                title = d.get("title", "")
                lines.append(f"- [{y}] [{lid}] {title}")

        filepath = CHARACTERS_DIR / f"{safe_name}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        created += 1

    print(f"✅ Character profiles → {CHARACTERS_DIR} ({created} files)")

    # ── 摘要 ─────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Analysis complete.")
    print(f"  Top keywords by decade (1840s vs 1870s):")
    for kw in ["revolution", "capital", "proletariat"]:
        kw_data = keyword_data.get(kw, [])
        val_1840s = sum(d["freq_per_10k"] for d in kw_data if 1840 <= d["year"] < 1850)
        val_1870s = sum(d["freq_per_10k"] for d in kw_data if 1870 <= d["year"] < 1880)
        print(f"    {kw:<15} 1840s: {val_1840s:.1f}  →  1870s: {val_1870s:.1f}")

    top_locations = location_counts.most_common(5)
    print(f"  Top locations: {', '.join(f'{n}({c})' for n,c in top_locations)}")


if __name__ == "__main__":
    analyze()
