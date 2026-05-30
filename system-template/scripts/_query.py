#!/usr/bin/env python3
"""
_query.py — [SYSTEM-NAME] CLI 查詢工具

用法:
    python scripts/_query.py stats          # 統計概覽
    python scripts/_query.py list           # 列出所有條目
    python scripts/_query.py search "關鍵詞" # 全文搜索
    python scripts/_query.py gap            # 分類缺口

依賴: data/compiled-{name}.json（由 _build-compiled-db.py 生成）
"""

import json, sys, os
from collections import Counter

# ## CUSTOMIZE HERE
SYSTEM_NAME = "my-system"
DB_PATH = f"data/compiled-{SYSTEM_NAME}.json"

# ## CUSTOMIZE HERE: 完整分類清單（用於 gap 命令）
ALL_CATEGORIES = ["cat-a", "cat-b"]


def load():
    if not os.path.exists(DB_PATH):
        print(f"❌ {DB_PATH} 不存在，請先執行 _build-compiled-db.py")
        sys.exit(1)
    return json.load(open(DB_PATH, 'r', encoding='utf-8'))


def cmd_stats(db):
    print(f"總條目: {db['_meta']['total']}")
    cats = Counter(e.get('category', '?') for e in db['entries'])
    for c, n in sorted(cats.items()):
        print(f"  {c}: {n}")


def cmd_list(db, args):
    for e in db['entries']:
        print(f"  [{e.get('category','?')}] {e['title'][:60]}")
        print(f"   id: {e['id']}")


def cmd_search(db, args):
    query = ' '.join(args)
    results = [e for e in db['entries'] if query in json.dumps(e, ensure_ascii=False)]
    for e in results:
        print(f"  [{e.get('category','?')}] {e['title'][:60]}")
        print(f"   id: {e['id']}")


def cmd_gap(db):
    existing = Counter(e.get('category', '?') for e in db['entries'])
    for cat in sorted(ALL_CATEGORIES):
        n = existing.get(cat, 0)
        bar = '█' * min(n, 20)
        print(f"  {cat}: {n:3d} {bar}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    db = load()
    cmd = sys.argv[1]
    args = sys.argv[2:]
    {'stats': cmd_stats, 'list': cmd_list, 'search': cmd_search, 'gap': cmd_gap}[cmd](db, args)
