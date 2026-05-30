#!/usr/bin/env python3
"""
_build-compiled-db.py — [SYSTEM-NAME] 編譯庫生成器

讀取 raw/ 下的所有 .md 檔案，提取 YAML Frontmatter + 正文摘要，
輸出為單一 compiled-{name}.json 供查詢與 Prefix 生成。

用法:
    python scripts/_build-compiled-db.py
"""

import json, glob, os

# ## CUSTOMIZE HERE: 修改你的系統名稱與路徑
SYSTEM_NAME = "my-system"
RAW_DIR = "raw"
OUTPUT_PATH = f"data/compiled-{SYSTEM_NAME}.json"

# ## CUSTOMIZE HERE: 定義要提取的 Frontmatter 欄位
FM_FIELDS = ["id", "category", "title", "title_en", "period",
             "key_figures", "key_concepts", "sources", "search_queries"]


def build():
    entries = []
    files = sorted(glob.glob(f"{RAW_DIR}/**/*.md", recursive=True))
    
    for fpath in files:
        if "_EXAMPLE" in fpath or fpath.endswith("_INDEX.md"):
            continue
        try:
            import yaml
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            parts = content.split('---', 2)
            if len(parts) < 3:
                continue
            fm = yaml.safe_load(parts[1])
            entry = {k: fm.get(k, '') for k in FM_FIELDS}
            # Flatten key_figures to names
            if isinstance(entry.get("key_figures"), list):
                entry["key_figures"] = [
                    f'{kf.get("name","")} ({kf.get("lifespan","")})'
                    if isinstance(kf, dict) else str(kf)
                    for kf in entry["key_figures"]
                ]
            entry["file"] = fpath
            entries.append(entry)
        except Exception as e:
            print(f"  ⚠️ {fpath}: {e}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    db = {"_meta": {"total": len(entries), "system": SYSTEM_NAME}, "entries": entries}
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"✅ {OUTPUT_PATH}: {len(entries)} entries")


if __name__ == "__main__":
    build()
