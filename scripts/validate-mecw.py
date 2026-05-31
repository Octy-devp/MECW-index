#!/usr/bin/env python3
"""
MECW 驗證器 v0.1（移植自 ECC validate-all-frontmatter.py 模式）
檢查：YAML語法、必填欄位、日期合理性、ID唯一性
"""
import json, sys
from pathlib import Path
from collections import defaultdict

COMPILED = Path("index/data/compiled-documents.json")

with open(COMPILED) as f:
    data = json.load(f)

docs = data["documents"]
errors = []
warnings = []

# ID唯一性（toc頁面允許多卷共用'index'）
ids = [d["id"] for d in docs]
dupes = [i for i in set(ids) if ids.count(i) > 1]
dupes = [i for i in dupes if not all(
    d.get("doc_type") in ("toc",) for d in docs if d["id"] == i
)]
if dupes:
    errors.append(f"Duplicate IDs (non-toc): {dupes}")

# 必填欄位
required = ["id", "title", "volume", "doc_type"]
missing = defaultdict(list)
for d in docs:
    for r in required:
        if not d.get(r):
            missing[r].append(d["id"])
for r, ids in missing.items():
    if ids:
        errors.append(f"Missing '{r}': {len(ids)} docs ({ids[:5]}...)")

# doc_type合法性
valid_types = {"letter", "article", "chapter", "paratext", "editorial", "hub", "toc"}
for d in docs:
    if d.get("doc_type") not in valid_types:
        errors.append(f"Invalid doc_type '{d['doc_type']}' in {d['id']}")

# 年份合理性
for d in docs:
    y = d.get("year")
    if y and isinstance(y, int):
        if y < 1000 or y > 2100:
            errors.append(f"Implausible year {y} in {d['id']}")

# 零字文檔（非 hub/toc）
for d in docs:
    if d.get("_word_count", 0) == 0 and d.get("doc_type") not in ("hub", "toc"):
        warnings.append(f"Zero-word doc (not hub/toc): {d['id']} - {d.get('title','')[:50]}")

# 統計
total = len(docs)
zero_body = sum(1 for d in docs if d.get("_word_count", 0) == 0)
has_year = sum(1 for d in docs if d.get("year") and isinstance(d.get("year"), int))

print(f"MECW Validation Report")
print(f"  Documents: {total}")
print(f"  With year: {has_year} ({has_year/total*100:.1f}%)")
print(f"  Zero body: {zero_body}")
print(f"  Errors:    {len(errors)}")
print(f"  Warnings:  {len(warnings)}")

if errors:
    print(f"\n❌ ERRORS:")
    for e in errors[:10]:
        print(f"  - {e}")
if warnings:
    print(f"\n⚠️ WARNINGS:")
    for w in warnings[:10]:
        print(f"  - {w}")

if not errors:
    print(f"\n✅ All validations passed")
    sys.exit(0)
else:
    sys.exit(1)
