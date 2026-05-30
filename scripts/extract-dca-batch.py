#!/usr/bin/env python3
"""
MECW DCA 批量提取器 v0.1
使用 Prefix v2（嵌入實例）+ compiled-db 準備 DCA 提取任務

用法：
  python scripts/extract-dca-batch.py --list          # 列出待提取文本
  python scripts/extract-dca-batch.py --prepare ID    # 準備單篇提取 prompt
  python scripts/extract-dca-batch.py --batch P0      # 準備 P0 優先級批次
"""

import json, argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent
COMPILED = ROOT / "index" / "data" / "compiled-documents.json"
PREFIX = ROOT / "index" / "data" / "mecw-prefix.txt"
CALIBRATION = ROOT / ".taskbook" / "dca-calibration-20.md"

def load_prefix():
    with open(PREFIX, "r") as f:
        return f.read()

def load_doc(doc_id):
    with open(COMPILED, "r") as f:
        data = json.load(f)
    for d in data["documents"]:
        if d["id"] == doc_id:
            return d
    return None

def load_doc_body(doc):
    filepath = ROOT / doc["_filepath"]
    if not filepath.exists():
        return None
    with open(filepath, "r") as f:
        content = f.read()
    parts = content.split("---", 2)
    return parts[2].strip() if len(parts) > 2 else content

def prepare_prompt(doc_id):
    """為一篇文本準備完整的 DCA 提取 prompt"""
    doc = load_doc(doc_id)
    if not doc:
        print(f"Document {doc_id} not found")
        return None

    prefix = load_prefix()
    body = load_doc_body(doc)

    # Truncate very long texts
    max_body_words = 10000
    words = body.split() if body else []
    if len(words) > max_body_words:
        body = " ".join(words[:max_body_words])
        body += f"\n\n[... truncated from {len(words)} words to {max_body_words}]"

    prompt = f"""{prefix}

---

## DOCUMENT TO ANALYZE

**ID**: {doc['id']}
**Title**: {doc.get('title', '')}
**Author**: {doc.get('author', '')}
**Year**: {doc.get('year', '')}
**Type**: {doc.get('doc_type', '')}

### TEXT:

{body}

---

## YOUR TASK

Extract the DCA structure from this text following the pattern
demonstrated in the worked examples above. Output as YAML.

CRITICAL: Be historically specific. Name actual events, people, institutions.
Do NOT use generic labels like 'crisis of methodology' or 'lag in theory' —
specify WHOSE methodology, WHAT theory, in WHAT historical conjuncture.
"""

    return prompt

def cmd_list():
    """列出待提取文本"""
    print("DCA Calibration Queue — 20 texts")
    print("=" * 60)
    
    # Parse the calibration file for status
    with open(CALIBRATION, "r") as f:
        content = f.read()
    
    # Count completed vs pending
    import re
    done = len(re.findall(r'✓.*?(?:已分析|A/B tested)', content))
    total = 20
    print(f"Completed: {done}/{total}")
    print(f"Remaining: {total - done}")
    
    print("\nQuick commands:")
    print("  python scripts/extract-dca-batch.py --prepare MECW11-004")
    print("  python scripts/extract-dca-batch.py --batch P0")

def cmd_prepare(doc_id):
    """準備單篇的 prompt"""
    doc = load_doc(doc_id)
    if not doc:
        print(f"✗ {doc_id} not found")
        return
    
    print(f"📄 {doc['id']}: [{doc.get('year')}] {doc.get('title','')[:80]}")
    print(f"   Author: {doc.get('author','?')}")
    print(f"   Words: {doc.get('_word_count',0)}")
    print(f"   Type: {doc.get('doc_type','?')}")
    
    prompt = prepare_prompt(doc_id)
    if prompt:
        out_path = ROOT / ".taskbook" / "dca-prompts" / f"{doc_id}.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"   ✅ Prompt saved: {out_path} ({len(prompt)} chars)")
    
    # Also print a short version for Copilot analysis
    body = load_doc_body(doc)
    if body:
        words = body.split()
        print(f"\n   --- Abbreviated body (first 200 words) ---")
        print("   " + " ".join(words[:200]))
        print(f"   ... ({len(words)} total words)")

def cmd_batch(priority):
    """準備一個優先級批次"""
    # Map priority to doc IDs
    batches = {
        "P0": ["MECW11-004", "MECW24-035", "MECW27-004"],
        "P1": ["MECW22-033", "MECW41-009", "MECW10-010", "MECW25-021", "MECW26-007"],
        "P2": ["MECW07-182", "MECW50-001"],
    }
    
    docs = batches.get(priority, [])
    print(f"Batch {priority}: {len(docs)} texts")
    for doc_id in docs:
        doc = load_doc(doc_id)
        if doc:
            w = doc.get('_word_count', 0)
            print(f"  {doc_id}: [{doc.get('year')}] {doc.get('title','')[:60]} ({w}w)")
    
    print(f"\nPrepare all? Run:")
    for doc_id in docs:
        print(f"  python scripts/extract-dca-batch.py --prepare {doc_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MECW DCA Batch Extractor")
    parser.add_argument("--list", action="store_true", help="List calibration queue")
    parser.add_argument("--prepare", type=str, help="Prepare prompt for document ID")
    parser.add_argument("--batch", type=str, choices=["P0","P1","P2"], help="Prepare priority batch")
    args = parser.parse_args()

    if args.list:
        cmd_list()
    elif args.prepare:
        cmd_prepare(args.prepare)
    elif args.batch:
        cmd_batch(args.batch)
    else:
        cmd_list()
