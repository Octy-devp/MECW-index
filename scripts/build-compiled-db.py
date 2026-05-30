#!/usr/bin/env python3
"""
MECW 文獻編譯器 v0.1
掃描 index/documents-raw/ 下所有 Markdown，提取 YAML frontmatter，
輸出單一 compiled-documents.json。

用法：
  python scripts/build-compiled-db.py
  python scripts/build-compiled-db.py --stats
"""

import os, sys, json, yaml, argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
DOCUMENTS_DIR = ROOT / "index" / "documents-raw"
OUTPUT = ROOT / "index" / "data" / "compiled-documents.json"

def parse_frontmatter(filepath):
    """從 Markdown 提取 YAML frontmatter + 統計 body"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None

    body = parts[2].strip()
    fm["_word_count"] = len(body.split()) if body else 0
    fm["_char_count"] = len(body) if body else 0
    fm["_filepath"] = str(filepath.relative_to(ROOT))

    return fm


def build():
    """掃描所有文獻，建立 compiled JSON"""
    documents = []
    errors = []
    stats = {
        "letters": 0, "articles": 0, "chapters": 0, "paratexts": 0, "editorials": 0, "other": 0,
        "volumes": set(),
        "years": [],
        "authors": set(),
    }

    for root, dirs, files in os.walk(DOCUMENTS_DIR):
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            filepath = Path(root) / f
            fm = parse_frontmatter(filepath)
            if fm is None:
                errors.append(str(filepath))
                continue

            doc_type = fm.get("doc_type", "unknown")
            if doc_type in stats:
                stats[doc_type] += 1
            else:
                stats["other"] += 1

            if fm.get("volume"):
                stats["volumes"].add(fm["volume"])
            if fm.get("year") and isinstance(fm["year"], int):
                stats["years"].append(fm["year"])
            if fm.get("author"):
                stats["authors"].add(fm["author"])

            documents.append(fm)

    # 排序：先 volume，再 id
    documents.sort(key=lambda d: (
        int(d.get("volume", 0)),
        d.get("id", "")
    ))

    # Compile
    compiled = {
        "_meta": {
            "version": "0.1.0",
            "built": datetime.now().isoformat(),
            "total_documents": len(documents),
            "volumes": sorted(stats["volumes"]),
            "volume_count": len(stats["volumes"]),
            "year_range": [min(stats["years"]), max(stats["years"])] if stats["years"] else None,
            "unique_authors": len(stats["authors"]),
            "type_distribution": {
                "letter": stats["letters"],
                "article": stats["articles"],
                "chapter": stats["chapters"],
                "paratext": stats["paratexts"],
                "editorial": stats["editorials"],
                "other": stats["other"],
            },
            "parse_errors": len(errors),
        },
        "documents": documents,
    }

    if errors:
        compiled["_meta"]["error_files"] = errors

    return compiled


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()

    compiled = build()
    meta = compiled["_meta"]

    if args.stats:
        print(f"📊 MECW Compiled Database")
        print(f"   Documents: {meta['total_documents']}")
        print(f"   Volumes:   {meta['volume_count']}")
        print(f"   Years:     {meta['year_range'][0]}–{meta['year_range'][1]}")
        print(f"   Authors:   {meta['unique_authors']}")
        print(f"   Letters:   {meta['type_distribution']['letter']}")
        print(f"   Articles:  {meta['type_distribution']['article']}")
        print(f"   Chapters:  {meta['type_distribution']['chapter']}")
        print(f"   Errors:    {meta['parse_errors']}")
    else:
        os.makedirs(OUTPUT.parent, exist_ok=True)
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(compiled, f, ensure_ascii=False, indent=2)
        size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
        print(f"✅ {OUTPUT}")
        print(f"   {meta['total_documents']} documents, {meta['volume_count']} volumes, {size_mb:.1f} MB")
