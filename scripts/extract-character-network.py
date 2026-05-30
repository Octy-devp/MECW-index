#!/usr/bin/env python3
"""
MECW 人物網絡提取器 v0.1
從 compiled-documents.json 中提取通信對象、建立人物索引。

用法：
  python scripts/extract-character-network.py
  python scripts/extract-character-network.py --top 30
"""

import json, re, os, argparse
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).parent.parent
COMPILED = ROOT / "index" / "data" / "compiled-documents.json"
CHARACTERS_DIR = ROOT / "index" / "characters"
OUTPUT = ROOT / "index" / "data" / "character-network.json"

def clean_name(name):
    """清理和標準化人名"""
    name = name.strip().rstrip('.').rstrip(',')
    # 移除多餘空白
    name = re.sub(r'\s+', ' ', name)
    # 首字母大寫（保留已有大寫）
    return name

def extract_recipient_from_title(title, author):
    """從書信標題中提取收信人"""
    # Pattern 1: "Letter to [Name], [Date]"
    m = re.match(r'Letter to (.+?),\s*(?:\d{1,2}\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December|early|late|mid|c\.|circa)', title)
    if m:
        return clean_name(m.group(1))

    # Pattern 2: "Letter to [Name]" (no date in title)
    m = re.match(r'Letter to (.+?)$', title)
    if m:
        return clean_name(m.group(1))

    # Pattern 3: "Letter to the [Title/Organization]"
    m = re.match(r'Letter to (the .+?),', title)
    if m:
        return clean_name(m.group(1))

    # Pattern 4: "From Marx to [Name]" or "Engels to [Name]"
    m = re.match(r'(?:Marx|Engels) to (.+?)\s+\d', title)
    if m:
        return clean_name(m.group(1))

    # Pattern 5: "To [Name]" or "[Author] to [Name]"
    m = re.match(r'(?:Karl\s+)?(?:Marx|Friedrich\s+)?(?:Engels)?\s*to\s+(.+?)\s+\d', title)
    if m:
        return clean_name(m.group(1))

    return None

def extract_recipient_from_archive_title(title):
    """從 archive 格式標題中提取收信人"""
    # "Engels to Pyotr Lavrov. 2 April"
    m = re.match(r'(?:Marx|Engels) to (.+?)\.\s*\d', title)
    if m:
        return clean_name(m.group(1))
    # "Marx to father in Trier"
    m = re.match(r'Marx to (.+?)$', title)
    if m:
        return clean_name(m.group(1))
    return None

def normalize_author(author):
    """標準化作者"""
    if not author:
        return "Unknown"
    if "karl marx" in author.lower() and "friedrich engels" not in author.lower():
        return "Karl Marx"
    if "friedrich engels" in author.lower() and "karl marx" not in author.lower():
        return "Friedrich Engels"
    if "karl marx" in author.lower() and "friedrich engels" in author.lower():
        return "Marx & Engels"
    return author

def extract():
    with open(COMPILED, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = data["documents"]
    letters = [d for d in documents if d.get("doc_type") == "letter"]
    print(f"Total letters: {len(letters)}")

    # 為每個通信對象建立檔案
    contacts = defaultdict(lambda: {
        "name": "",
        "letters_received": 0,
        "letters_from_marx": 0,
        "letters_from_engels": 0,
        "letters_from_both": 0,
        "first_year": 9999,
        "last_year": 0,
        "letter_ids": [],
    })

    unmatched = []

    for doc in letters:
        title = doc.get("title", "")
        author = normalize_author(doc.get("author", ""))
        year = doc.get("year")
        doc_id = doc.get("id", "")

        # 嘗試提取收信人
        recipient = extract_recipient_from_title(title, author)
        if not recipient:
            recipient = extract_recipient_from_archive_title(title)

        if not recipient:
            unmatched.append({"id": doc_id, "title": title, "author": author})
            continue

        # 更新聯絡人統計
        contact = contacts[recipient]
        contact["name"] = recipient
        contact["letters_received"] += 1
        contact["letter_ids"].append(doc_id)

        if "Marx" in author and "Engels" in author:
            contact["letters_from_both"] += 1
        elif "Marx" in author:
            contact["letters_from_marx"] += 1
        elif "Engels" in author:
            contact["letters_from_engels"] += 1

        if year and isinstance(year, int):
            contact["first_year"] = min(contact["first_year"], year)
            contact["last_year"] = max(contact["last_year"], year)

    # 排序：依收到信件數
    sorted_contacts = sorted(contacts.items(), key=lambda x: x[1]["letters_received"], reverse=True)

    # 輸出
    result = {
        "_meta": {
            "total_letters_analyzed": len(letters),
            "unique_contacts": len(contacts),
            "unmatched_titles": len(unmatched),
            "match_rate": f"{(len(letters) - len(unmatched)) / len(letters) * 100:.1f}%",
        },
        "contacts": [{"name": name, **info} for name, info in sorted_contacts],
        "unmatched": unmatched[:20],  # 只保留前 20 個未匹配
    }

    return result

def print_top(result, n=30):
    """打印 Top N 通信對象"""
    contacts = result["contacts"]
    print(f"\n{'='*70}")
    print(f"  Top {n} 通信對象（按收到信件數排序）")
    print(f"{'='*70}")
    print(f"{'#':<4} {'Name':<40} {'Letters':>8} {'Period':>12}")
    print(f"{'-'*70}")

    for i, c in enumerate(contacts[:n], 1):
        name = c["name"][:38]
        count = c["letters_received"]
        period = f"{c['first_year']}-{c['last_year']}" if c['first_year'] < 9999 else "N/A"
        print(f"{i:<4} {name:<40} {count:>8} {period:>12}")

    print(f"\n  Match rate: {result['_meta']['match_rate']}")
    print(f"  Unique contacts: {result['_meta']['unique_contacts']}")
    print(f"  Unmatched: {result['_meta']['unmatched_titles']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=30, help="Show top N contacts")
    parser.add_argument("--save", action="store_true", help="Save to JSON")
    args = parser.parse_args()

    result = extract()
    print_top(result, args.top)

    if args.save:
        os.makedirs(OUTPUT.parent, exist_ok=True)
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Saved to {OUTPUT}")
