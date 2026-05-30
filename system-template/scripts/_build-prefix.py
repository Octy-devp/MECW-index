#!/usr/bin/env python3
"""
_build-prefix.py — [SYSTEM-NAME] AI Prefix 生成器

從 compiled-{name}.json 生成濃縮索引文本，供 AI Agent 載入。

用法:
    python scripts/_build-prefix.py
"""

import json, os
from collections import defaultdict

# ## CUSTOMIZE HERE
SYSTEM_NAME = "my-system"
DB_PATH = f"data/compiled-{SYSTEM_NAME}.json"
OUTPUT_PATH = f"data/{SYSTEM_NAME}-prefix.txt"

# ## CUSTOMIZE HERE: 分類名稱對照表
CAT_NAMES = {
    "cat-a": "分類 A",
    "cat-b": "分類 B",
}


def estimate_tokens(text: str) -> int:
    chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or '\u3000' <= c <= '\u303f')
    return int(chinese * 0.6 + (len(text) - chinese) * 0.25)


def build():
    if not os.path.exists(DB_PATH):
        print("❌ 請先執行 _build-compiled-db.py")
        return
    
    db = json.load(open(DB_PATH, 'r', encoding='utf-8'))
    entries = db.get("entries", [])
    
    # ## CUSTOMIZE HERE: 修改系統提示詞
    prompt = f"""你是 {SYSTEM_NAME} 的分析師。
以下是 {SYSTEM_NAME} 的索引摘要（{len(entries)} 條目）。
請先查本索引定位相關條目，再讀取 raw/ 下的對應檔案。"""

    lines = [prompt, "", "=" * 60]
    lines.append(f"## {SYSTEM_NAME} 索引（{len(entries)} 條目）\n")
    
    cats = defaultdict(list)
    for e in entries:
        cats[e.get("category", "?")].append(e)
    
    for cat in sorted(cats.keys()):
        cat_entries = cats[cat]
        label = CAT_NAMES.get(cat, cat)
        lines.append(f"### {label}（{len(cat_entries)} 篇）")
        for e in cat_entries:
            concepts = ", ".join(e.get("key_concepts", [])[:3])
            lines.append(f"  `{e['id']}` — {e['title'][:60]}")
            if concepts:
                lines.append(f"    ↳ {concepts}")
        lines.append("")
    
    full = "\n".join(lines)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    open(OUTPUT_PATH, 'w', encoding='utf-8').write(full)
    print(f"✅ {OUTPUT_PATH}: {len(full):,} chars, ~{estimate_tokens(full):,} tokens")


if __name__ == "__main__":
    build()
