#!/usr/bin/env python3
"""
MECW 查詢工具 v0.1
基於 compiled-documents.json 的 CLI 查詢。

用法：
  python scripts/query.py --author "Karl Marx" --year 1848
  python scripts/query.py --contact "Friedrich Engels" --top 10
  python scripts/query.py --timeline
  python scripts/query.py --stats
"""

import json, argparse, sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).parent.parent
COMPILED = ROOT / "index" / "data" / "compiled-documents.json"
NETWORK = ROOT / "index" / "data" / "character-network.json"

def load_data():
    with open(COMPILED, "r") as f:
        data = json.load(f)
    return data

def load_network():
    if NETWORK.exists():
        with open(NETWORK, "r") as f:
            return json.load(f)
    return None

def cmd_stats(data):
    meta = data["_meta"]
    print(f"📊 MECW Statistics")
    print(f"   Total documents: {meta['total_documents']}")
    print(f"   Volumes:         {meta['volume_count']} (1–50)")
    print(f"   Year range:      {meta['year_range'][0]}–{meta['year_range'][1]}")
    print(f"   Unique authors:  {meta['unique_authors']}")
    print(f"   Type distribution:")
    for t, c in meta["type_distribution"].items():
        if c > 0:
            print(f"     {t:<12} {c:>6}")

def cmd_author(data, author, top=20, year=None):
    docs = data["documents"]
    author_lower = author.lower()
    matches = []

    for d in docs:
        d_author = (d.get("author") or "").lower()
        if author_lower in d_author:
            if year and d.get("year") != year:
                continue
            matches.append(d)

    matches.sort(key=lambda d: d.get("year", 0) or 0)
    print(f"📨 {author}: {len(matches)} documents")
    for d in matches[:top]:
        y = d.get("year", "?")
        t = d.get("doc_type", "?")
        title = (d.get("title") or "")[:80]
        print(f"  [{y}] [{t}] {title}")

def cmd_contact(data, network, name, top=20):
    """查詢與某人的通信"""
    if not network:
        print("Character network not built. Run extract-character-network.py first.")
        return

    contacts = {c["name"]: c for c in network["contacts"]}
    contact = contacts.get(name)
    if not contact:
        # 模糊搜索
        matches = [(n, c) for n, c in contacts.items() if name.lower() in n.lower()]
        if matches:
            print(f"🔍 Found {len(matches)} matching contacts:")
            for n, c in sorted(matches, key=lambda x: x[1]["letters_received"], reverse=True)[:10]:
                print(f"  {n} ({c['letters_received']} letters)")
            return
        print(f"Contact '{name}' not found.")
        return

    print(f"📬 {name}")
    print(f"   Letters received: {contact['letters_received']}")
    print(f"   From Marx: {contact['letters_from_marx']}, From Engels: {contact['letters_from_engels']}")
    print(f"   Period: {contact['first_year']}–{contact['last_year']}")
    print(f"   Recent letters:")
    docs = {d["id"]: d for d in data["documents"]}
    for lid in contact["letter_ids"][-top:]:
        d = docs.get(lid)
        if d:
            y = d.get("year", "?")
            title = (d.get("title") or "")[:80]
            print(f"     [{y}] {title}")

def cmd_timeline(data, decade=False):
    """按年/十年統計文獻數量"""
    docs = data["documents"]
    year_counts = Counter()
    for d in docs:
        y = d.get("year")
        if y and isinstance(y, int) and 1835 <= y <= 1895:
            year_counts[y] += 1

    if decade:
        decade_counts = Counter()
        for y, c in year_counts.items():
            decade_counts[(y // 10) * 10] += c
        print("📅 Documents by decade:")
        for dec in sorted(decade_counts):
            bar = "█" * (decade_counts[dec] // 20)
            print(f"  {dec}s: {decade_counts[dec]:>5} {bar}")
    else:
        print("📅 Documents by year (1835–1895):")
        max_c = max(year_counts.values())
        for y in sorted(year_counts):
            if year_counts[y] > 5:
                bar = "█" * (year_counts[y] * 50 // max_c)
                print(f"  {y}: {year_counts[y]:>4} {bar}")

    # 高峰年
    top_years = year_counts.most_common(10)
    print(f"\n  Peak years: {', '.join(f'{y}({c})' for y,c in top_years)}")

def cmd_volume(data, vol):
    """列出某卷的所有文獻"""
    docs = [d for d in data["documents"] if d.get("volume") == vol]
    docs.sort(key=lambda d: d.get("id", ""))
    print(f"📚 Volume {vol}: {len(docs)} documents")
    for d in docs:
        y = d.get("year", "?")
        t = d.get("doc_type", "?")
        title = (d.get("title") or "")[:80]
        print(f"  [{y}] [{t}] {title}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MECW Query Tool")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--author", type=str)
    parser.add_argument("--year", type=int)
    parser.add_argument("--contact", type=str)
    parser.add_argument("--volume", type=int)
    parser.add_argument("--timeline", action="store_true")
    parser.add_argument("--decade", action="store_true")
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    data = load_data()
    network = load_network()

    if args.stats:
        cmd_stats(data)
    elif args.contact:
        cmd_contact(data, network, args.contact, args.top)
    elif args.author:
        cmd_author(data, args.author, args.top, args.year)
    elif args.timeline or args.decade:
        cmd_timeline(data, args.decade)
    elif args.volume:
        cmd_volume(data, args.volume)
    else:
        cmd_stats(data)
        print("\nUsage: python scripts/query.py [--stats|--author|--contact|--timeline|--volume]")
