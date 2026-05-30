#!/usr/bin/env python3
"""
_validate-schema.py — [SYSTEM-NAME] Schema 驗證器

檢查 raw/ 下所有 .md 的 Frontmatter 是否符合 _SCHEMA.md 規範。

用法:
    python scripts/_validate-schema.py
"""

import glob, os

# ## CUSTOMIZE HERE: 必填欄位清單
REQUIRED_FIELDS = ["id", "category", "title", "key_concepts", "key_figures", "sources"]
RAW_DIR = "raw"


def validate():
    files = sorted(glob.glob(f"{RAW_DIR}/**/*.md", recursive=True))
    errors = 0
    warnings = 0
    
    for fpath in files:
        if "_EXAMPLE" in fpath or "_INDEX" in fpath:
            continue
        try:
            import yaml
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            parts = content.split('---', 2)
            if len(parts) < 3:
                print(f"🔴 {fpath}: 無有效 Frontmatter")
                errors += 1
                continue
            fm = yaml.safe_load(parts[1])
            missing = [f for f in REQUIRED_FIELDS if f not in fm]
            if missing:
                print(f"🔴 {fpath}: 缺少 {missing}")
                errors += 1
            else:
                figures = len(fm.get("key_figures", []))
                sources = len(fm.get("sources", []))
                if figures == 0:
                    print(f"🟡 {fpath}: key_figures 為空")
                    warnings += 1
                if sources == 0:
                    print(f"🟡 {fpath}: sources 為空")
                    warnings += 1
        except Exception as e:
            print(f"🔴 {fpath}: {e}")
            errors += 1
    
    print(f"\n{'✅ 全部通過' if errors == 0 else f'🔴 {errors} errors, {warnings} warnings'}")


if __name__ == "__main__":
    validate()
