#!/usr/bin/env python3
"""
MECW Prefix 格式發射器 v0.1
將 canonical prefix (Markdown) 轉換為不同 LLM 平台的最佳格式。

用法：
  python scripts/emit-prefix.py --target deepseek   # Full Markdown (default)
  python scripts/emit-prefix.py --target claude     # XML Semantic Layering
  python scripts/emit-prefix.py --target gpt        # XML-Tagged Markdown
  python scripts/emit-prefix.py --target all        # All three

基於 SkCC (arxiv 2605.03353) 的格式敏感性發現：
  - Claude: XML tags → +23% accuracy
  - GPT: XML-tagged Markdown → avoids JSON format tax
  - DeepSeek: Full Markdown → ultra-long context, no truncation
"""

import json, argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
PREFIX_SRC = ROOT / "index" / "data" / "mecw-prefix.txt"
OUT_DIR = ROOT / "index" / "data" / "prefix-emitted"

def load_prefix():
    with open(PREFIX_SRC, "r") as f:
        return f.read()

def emit_markdown(prefix):
    """DeepSeek / Kimi: Full Markdown Preservation"""
    return prefix  # 原生格式，不改動

def emit_xml(prefix):
    """Claude: XML Semantic Layering"""
    sections = prefix.split("\n## ")
    xml_parts = ['<mecw_index xmlns="https://ecc-project.org/mecw">']
    xml_parts.append('  <system_info>')
    xml_parts.append(f'    <chamber>Second Chamber — MECW-index</chamber>')
    xml_parts.append(f'    <architecture>Two-Chamber Soviet ∥ ECC (Chamber 1)</architecture>')
    xml_parts.append(f'    <built>{datetime.now().isoformat()}</built>')
    xml_parts.append('  </system_info>')

    for section in sections[1:]:  # skip header
        lines = section.strip().split("\n")
        if not lines:
            continue
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()

        # Map sections to XML tags
        tag_map = {
            "WORKED EXAMPLE": "worked_example",
            "YOUR TASK": "task_instruction",
            "QUICK REFERENCE": "quick_reference",
            "PROJECT DEFINITION": "project_definition",
            "CORE THEORETICAL FRAMEWORK": "theoretical_framework",
            "HISTORICAL PERIODS": "historical_periods",
            "KEY FIGURES": "key_figures",
            "CORPUS STATISTICS": "corpus_statistics",
            "DOCUMENT TYPES": "document_types",
            "DCA ANALYSIS FRAMEWORK": "dca_framework",
            "OUTPUT FORMAT": "output_format",
        }

        tag = tag_map.get(title.replace("1. ", "").replace("2. ", ""), "section")
        xml_parts.append(f'  <{tag} category="{title}">')
        for line in body.split("\n"):
            if line.strip():
                xml_parts.append(f'    <content>{line.strip()}</content>')
        xml_parts.append(f'  </{tag}>')

    xml_parts.append('</mecw_index>')
    return "\n".join(xml_parts)

def emit_xml_markdown(prefix):
    """GPT/Codex: XML-Tagged Markdown (hybrid)"""
    sections = prefix.split("\n## ")
    parts = [sections[0]]  # header

    for section in sections[1:]:
        lines = section.strip().split("\n")
        if not lines:
            continue
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()

        parts.append(f'<section category="{title}">')
        parts.append(body)
        parts.append('</section>')
        parts.append('')

    return "\n".join(parts)

def emit_all(prefix):
    """Emit all formats"""
    formats = {
        "deepseek": ("mecw-prefix-deepseek.txt", emit_markdown),
        "claude": ("mecw-prefix-claude.txt", emit_xml),
        "gpt": ("mecw-prefix-gpt.txt", emit_xml_markdown),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    for name, (filename, emitter) in formats.items():
        content = emitter(prefix)
        out_path = OUT_DIR / filename
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        size = len(content)
        results[name] = {"file": str(out_path), "size": size, "tokens_est": len(content.split())}

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MECW Prefix Format Emitter")
    parser.add_argument("--target", choices=["deepseek", "claude", "gpt", "all"],
                        default="all")
    args = parser.parse_args()

    prefix = load_prefix()

    if args.target == "all":
        results = emit_all(prefix)
        print("✅ Prefix emitted for all targets:")
        for name, info in results.items():
            print(f"   {name}: {info['size']} chars, ~{info['tokens_est']} tokens")
    elif args.target == "deepseek":
        content = emit_markdown(prefix)
        out = OUT_DIR / "mecw-prefix-deepseek.txt"
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            f.write(content)
        print(f"✅ DeepSeek → {out} ({len(content)} chars)")
    elif args.target == "claude":
        content = emit_xml(prefix)
        out = OUT_DIR / "mecw-prefix-claude.txt"
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            f.write(content)
        print(f"✅ Claude → {out} ({len(content)} chars)")
    elif args.target == "gpt":
        content = emit_xml_markdown(prefix)
        out = OUT_DIR / "mecw-prefix-gpt.txt"
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            f.write(content)
        print(f"✅ GPT → {out} ({len(content)} chars)")
