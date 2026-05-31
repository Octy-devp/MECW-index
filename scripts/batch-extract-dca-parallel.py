#!/usr/bin/env python3
"""
batch-extract-dca-parallel.py — 並發 DCA 全庫提取引擎 v1.0

用法：
  # 校準批次（50 篇）
  python scripts/batch-extract-dca-parallel.py --sample 50 --workers 10
  
  # 全庫提取（所有 articles + chapters，不含已提取）
  python scripts/batch-extract-dca-parallel.py --all --workers 10
  
  # 指定年份範圍
  python scripts/batch-extract-dca-parallel.py --years 1848,1871,1875 --workers 5
  
  # 從文件讀取 ID 列表
  python scripts/batch-extract-dca-parallel.py --ids ids.txt --workers 10
  
  # 只顯示計劃（dry-run）
  python scripts/batch-extract-dca-parallel.py --all --dry-run

環境變數：DEEPSEEK_API_KEY
"""

import argparse, json, os, sys, time, random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from collections import Counter

ROOT = Path(__file__).parent.parent
COMPILED = ROOT / "index" / "data" / "compiled-documents.json"
PREFIX_PATH = ROOT / "index" / "data" / "mecw-prefix.txt"
DOCS_DIR = ROOT / "index" / "documents-raw"
OUT_DIR = ROOT / ".taskbook" / "dca-results"

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

def already_extracted(doc_id):
    return (OUT_DIR / f"{doc_id}.yaml").exists()

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

def build_dca_prompt(doc, prefix):
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

# ── 提取器（線程安全） ─────────────────────────────

class Stats:
    def __init__(self):
        self.success = 0
        self.error = 0
        self.skipped = 0
        self.total_tokens = 0
        self.total_input = 0
        self.total_output = 0
        self.start_time = time.time()

    def elapsed(self):
        return time.time() - self.start_time

    def summary(self):
        e = self.elapsed()
        rate = self.success / e if e > 0 else 0
        return (f"✅ {self.success} | ❌ {self.error} | ⏭️ {self.skipped} | "
                f"⏱️ {e:.0f}s ({rate:.1f}/s) | "
                f"🪙 {self.total_tokens} tokens (in={self.total_input} out={self.total_output})")

stats = Stats()

def extract_one(doc_id, db, prefix):
    """提取單篇 DCA，返回 (doc_id, status, tokens, error_msg)"""
    if already_extracted(doc_id):
        return (doc_id, "skipped", 0, None)

    doc = None
    for d in db["documents"]:
        if d["id"] == doc_id:
            doc = d
            break
    if not doc:
        return (doc_id, "error", 0, f"not found in db")

    prompt = build_dca_prompt(doc, prefix)
    result = call_deepseek(prompt, max_tokens=4096)

    if "error" in result:
        return (doc_id, "error", 0, result["error"])

    # Save result
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{doc_id}.yaml"
    with open(out_path, "w") as f:
        f.write(result["content"])

    usage = result.get("usage", {})
    tokens = usage.get("total_tokens", 0)
    inp = usage.get("prompt_tokens", 0)
    out = usage.get("completion_tokens", 0)
    return (doc_id, "success", tokens, None)

# ── 主流程 ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MECW Parallel DCA Batch Extractor")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--sample", type=int, help="Random sample size (for calibration)")
    g.add_argument("--all", action="store_true", help="All DCA-worthy docs (articles+chapters)")
    g.add_argument("--ids", type=str, help="File with doc IDs, one per line")
    g.add_argument("--years", type=str, help="Comma-separated years, e.g. 1848,1871,1875")
    parser.add_argument("--workers", type=int, default=5, help="Concurrent workers (default: 5)")
    parser.add_argument("--dry-run", action="store_true", help="Show plan only, don't extract")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="Skip already-extracted docs")
    parser.add_argument("--force", action="store_true", help="Re-extract even if exists")
    parser.add_argument("--delay", type=float, default=0.1, help="Inter-request delay in seconds (default: 0.1)")
    args = parser.parse_args()

    db = load_db()
    prefix = load_prefix()
    if not prefix:
        print("❌ Prefix not found. Run build-mecw-prefix.py first.")
        sys.exit(1)

    # Build doc list
    all_docs = db["documents"]
    
    if args.all:
        # DCA-worthy: articles + chapters
        candidates = [d for d in all_docs if d.get("doc_type") in ("article", "chapter")]
    elif args.sample:
        # Random sample from DCA-worthy
        worthy = [d for d in all_docs if d.get("doc_type") in ("article", "chapter")]
        candidates = random.sample(worthy, min(args.sample, len(worthy)))
    elif args.years:
        years = set(int(y.strip()) for y in args.years.split(","))
        candidates = [d for d in all_docs if d.get("year") in years 
                      and d.get("doc_type") in ("article", "chapter")]
    elif args.ids:
        with open(args.ids) as f:
            ids = [line.strip() for line in f if line.strip()]
        id_set = set(ids)
        candidates = [d for d in all_docs if d["id"] in id_set]
    else:
        candidates = []

    # Filter already-extracted
    if not args.force:
        new_candidates = []
        skipped = 0
        for d in candidates:
            if already_extracted(d["id"]):
                skipped += 1
            else:
                new_candidates.append(d)
        if skipped:
            print(f"⏭️  Skipping {skipped} already-extracted docs")
        candidates = new_candidates

    print(f"\n{'='*60}")
    print(f"MECW Parallel DCA Extractor")
    print(f"  Model: {DEEPSEEK_MODEL}")
    print(f"  Workers: {args.workers}")
    print(f"  Candidates: {len(candidates)}")
    print(f"  Output: {OUT_DIR}/")
    
    # Show year distribution
    years = Counter(d.get("year") for d in candidates)
    top_years = years.most_common(5)
    print(f"  Top years: {', '.join(f'{y}({c})' for y,c in top_years)}")
    print(f"{'='*60}\n")

    if args.dry_run:
        print("DRY RUN — showing first 10 candidates:")
        for d in candidates[:10]:
            print(f"  [{d.get('year','?')}] {d['id']}: {d.get('title','')[:70]}")
        print(f"  ... and {len(candidates)-10} more")
        return

    if not candidates:
        print("✅ Nothing to extract — all done!")
        return

    doc_ids = [d["id"] for d in candidates]
    print(f"🚀 Starting {len(doc_ids)} extractions with {args.workers} workers...\n")

    # Report progress periodically
    last_report = time.time()
    report_interval = 5  # seconds

    def report():
        nonlocal last_report
        now = time.time()
        if now - last_report >= report_interval:
            print(f"  [{stats.elapsed():.0f}s] {stats.summary()}")
            last_report = now

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for doc_id in doc_ids:
            # Stagger submission to avoid burst
            future = executor.submit(extract_one, doc_id, db, prefix)
            futures[future] = doc_id
            time.sleep(args.delay)

        for future in as_completed(futures):
            doc_id, status, tokens, err = future.result()
            if status == "success":
                stats.success += 1
                stats.total_tokens += tokens
            elif status == "error":
                stats.error += 1
                if err:
                    print(f"  ❌ {doc_id}: {err[:80]}")
            else:
                stats.skipped += 1
            
            report()

    print(f"\n{'='*60}")
    print(f"🏁 COMPLETE: {stats.summary()}")
    
    # Cost estimate (DeepSeek V4 Pro pricing ~similar to chat)
    # Input: $0.27/1M, Output: $1.10/1M (conservative, actual may differ)
    # The stats track total tokens but we don't have input/output split per call
    # Rough estimate: total_tokens * $0.50/1M (blended)
    est_cost = stats.total_tokens / 1_000_000 * 0.50
    print(f"💵 Estimated cost: ${est_cost:.3f}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
