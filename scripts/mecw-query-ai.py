#!/usr/bin/env python3
"""
mecw-query-ai.py — MECW 語義查詢引擎 v0.1
移植自 ecc-query-ai.py，適配 MECW compiled-documents.json + mecw-prefix.txt

兩級查詢：
  1. compiled-db 結構化初篩（本地，免費）
  2. Prefix + 文獻全文 → DeepSeek API 語義分析 / DCA 提取

用法：
  python scripts/mecw-query-ai.py "Marx's view on the Paris Commune" --api
  python scripts/mecw-query-ai.py --dca MECW35-004
  python scripts/mecw-query-ai.py --dca-batch P1 --api

環境變數：
  DEEPSEEK_API_KEY  — DeepSeek API 密鑰（--api 模式必需）
"""

import argparse, json, os, sys, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).parent.parent
COMPILED = ROOT / "index" / "data" / "compiled-documents.json"
PREFIX_PATH = ROOT / "index" / "data" / "mecw-prefix.txt"
DOCS_DIR = ROOT / "index" / "documents-raw"

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-v4-pro"

# ── 加載 ───────────────────────────────────────────

def load_db():
    with open(COMPILED, "r") as f:
        return json.load(f)

def load_prefix():
    if PREFIX_PATH.exists():
        with open(PREFIX_PATH, "r") as f:
            return f.read()
    return ""

def load_doc_body(doc):
    fp = doc.get("_filepath")
    if not fp:
        return ""
    path = ROOT / fp
    if not path.exists():
        return ""
    with open(path, "r") as f:
        content = f.read()
    parts = content.split("---", 2)
    return parts[2].strip() if len(parts) > 2 else content

# ── 查詢 ───────────────────────────────────────────

def search_docs(db, query, limit=10):
    """本地全文搜索"""
    q = query.lower()
    results = []
    for d in db["documents"]:
        title = (d.get("title") or "").lower()
        author = (d.get("author") or "").lower()
        body = ""
        if q in title or q in author:
            results.append(d)
        elif len(results) < limit * 3:
            body = load_doc_body(d)[:2000].lower()
            if q in body:
                results.append(d)
        if len(results) >= limit:
            break
    return results[:limit]

# ── API ────────────────────────────────────────────

def call_deepseek(prompt, max_tokens=4096):
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return {"error": "DEEPSEEK_API_KEY not set"}

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "You are a Marxist philologist. Extract DCA structure from Marx/Engels texts. Output valid YAML only."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0,
    }

    req = Request(DEEPSEEK_API_URL,
                  data=json.dumps(payload).encode("utf-8"),
                  headers={
                      "Authorization": f"Bearer {api_key}",
                      "Content-Type": "application/json",
                  })

    try:
        with urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode())
            return {
                "content": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {}),
                "model": result.get("model", ""),
            }
    except HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}

# ── DCA 提取 ───────────────────────────────────────

def build_dca_prompt(doc, prefix):
    """構建單篇 DCA 提取 prompt"""
    body = load_doc_body(doc)
    words = body.split()
    if len(words) > 8000:
        body = " ".join(words[:8000]) + f"\n\n[... truncated from {len(words)} words]"

    return f"""{prefix}

---

## DOCUMENT TO ANALYZE

**ID**: {doc['id']}
**Title**: {doc.get('title', '')}
**Author**: {doc.get('author', '')}
**Year**: {doc.get('year', '')}

### TEXT:

{body}

---

Extract the DCA structure following the worked examples above.
Include `reasoning` (Chain-of-Thought) before the structured YAML.
Output valid YAML only (no markdown wrapping).
"""

def extract_dca(doc_id, prefix, db):
    """提取單篇 DCA"""
    doc = None
    for d in db["documents"]:
        if d["id"] == doc_id:
            doc = d
            break
    if not doc:
        return f"Document {doc_id} not found"

    prompt = build_dca_prompt(doc, prefix)
    result = call_deepseek(prompt, max_tokens=4096)

    if "error" in result:
        return f"API Error: {result['error']}"

    # Save result
    out_dir = ROOT / ".taskbook" / "dca-results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{doc_id}.yaml"
    with open(out_path, "w") as f:
        f.write(result["content"])

    tokens = result.get("usage", {}).get("total_tokens", "?")
    return f"✅ {doc_id} → {out_path} ({tokens} tokens)"

def extract_dca_batch(doc_ids, prefix, db):
    """批量 DCA 提取"""
    results = []
    for i, doc_id in enumerate(doc_ids, 1):
        print(f"  [{i}/{len(doc_ids)}] {doc_id}...", end=" ", flush=True)
        result = extract_dca(doc_id, prefix, db)
        print(result.split("\n")[0])
        results.append(result)
        if i < len(doc_ids):
            time.sleep(0.5)  # rate limit
    return results

# ── CLI ────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MECW Query + DCA Extraction")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--api", action="store_true", help="Use DeepSeek API")
    parser.add_argument("--dca", type=str, help="Extract DCA for document ID")
    parser.add_argument("--dca-batch", type=str, choices=["P0","P1","P2"],
                        help="Batch DCA extraction by priority")
    parser.add_argument("--top", type=int, default=10, help="Max search results")
    parser.add_argument("--limit", type=int, default=3, help="Max docs to send to API")
    args = parser.parse_args()

    db = load_db()
    prefix = load_prefix()

    if args.dca:
        print(extract_dca(args.dca, prefix, db))

    elif args.dca_batch:
        batches = {
            "P0": ["MECW11-004", "MECW24-035", "MECW27-004"],
            "P1": ["MECW22-033", "MECW41-009", "MECW10-010", "MECW25-021", "MECW26-007"],
            "P2": ["MECW07-182", "MECW50-001"],
        }
        doc_ids = batches.get(args.dca_batch, [])
        print(f"DCA Batch: {args.dca_batch} ({len(doc_ids)} docs)")
        extract_dca_batch(doc_ids, prefix, db)

    elif args.query:
        results = search_docs(db, args.query, args.top)
        print(f"🔍 '{args.query}': {len(results)} results")
        for d in results[:args.top]:
            y = d.get("year", "?")
            t = d.get("doc_type", "?")
            title = (d.get("title") or "")[:80]
            print(f"  [{y}] [{t}] {d['id']}: {title}")

        if args.api and results:
            print(f"\n🤖 Sending top {min(args.limit, len(results))} to DeepSeek...")
            for d in results[:args.limit]:
                prompt = build_dca_prompt(d, prefix)
                result = call_deepseek(prompt)
                if "error" in result:
                    print(f"  ✗ {d['id']}: {result['error']}")
                else:
                    print(f"  ✓ {d['id']}: {result.get('usage',{}).get('total_tokens','?')} tokens")
                    print(f"    {result['content'][:200]}...")

    else:
        print("MECW Query Tool")
        print(f"  {db['_meta']['total_documents']} documents in {db['_meta']['volume_count']} volumes")
        print(f"  Prefix: {'loaded' if prefix else 'not found'} ({len(prefix)} chars)")
        print(f"\nUsage:")
        print(f"  python scripts/mecw-query-ai.py 'Paris Commune'")
        print(f"  python scripts/mecw-query-ai.py --dca MECW35-004")
        print(f"  python scripts/mecw-query-ai.py --dca-batch P1 --api")
