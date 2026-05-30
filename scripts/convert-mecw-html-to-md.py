#!/usr/bin/env python3
"""
MECW HTML → Markdown 轉換器 v0.1
將 en/MECW/{volume}/*.html 轉為帶 YAML frontmatter 的 Markdown 文件

用法：
  python scripts/convert-mecw-html-to-md.py --volume 1 --dry-run
  python scripts/convert-mecw-html-to-md.py --volume all --limit 10
"""

import os, sys, re, argparse
from pathlib import Path
from html.parser import HTMLParser

# ── 配置 ──────────────────────────────────────────────
SOURCE_DIR = "/workspaces/MECW-source/en/MECW"
OUTPUT_DIR = "/workspaces/MECW-index/index/documents-raw"

# ── HTML 解析器 ───────────────────────────────────────

class MECWParser(HTMLParser):
    """提取 <h1>, HeaderTable, <p> 內容，轉為 Markdown"""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.author = ""
        self.written = ""
        self.publication = ""
        self.body_parts = []

        # 狀態機
        self._in_h1 = False
        self._in_header_cell = False
        self._header_key = ""
        self._header_value = ""
        self._in_publication = False
        self._in_p = False
        self._current_p = ""
        self._skip_divs = {"GlobalSummary", "subpagelist", "mw-references-wrap"}
        self._skip_depth = 0
        self._skip_tag = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if self._skip_depth > 0:
            self._skip_depth += 1
            return

        # 跳過目錄、參考文獻區塊
        if tag == "div" and attrs_dict.get("id") in self._skip_divs:
            self._skip_depth = 1
            self._skip_tag = attrs_dict["id"]
            return
        if tag == "div" and attrs_dict.get("class") in self._skip_divs:
            self._skip_depth = 1
            self._skip_tag = attrs_dict["class"]
            return

        # <h1 class="firstHeading">
        if tag == "h1" and "firstHeading" in attrs_dict.get("class", ""):
            self._in_h1 = True

        # <table class="HeaderTable"> → 提取 Author/Written
        if tag == "th" and self._in_header_table:
            self._in_header_cell = True
            self._header_key = ""
        if tag == "td" and self._in_header_table:
            self._in_header_cell = True
            self._header_value = ""

        # <div class="Publication">
        if tag == "div" and attrs_dict.get("class") == "Publication":
            self._in_publication = True

        # <p>
        if tag == "p":
            self._in_p = True
            self._current_p = ""

        # inline formatting
        if tag == "i" or tag == "em":
            self._current_p += "*"
        if tag == "b" or tag == "strong":
            self._current_p += "**"
        if tag == "br":
            self._current_p += "\n"

    def handle_endtag(self, tag):
        if self._skip_depth > 0:
            self._skip_depth -= 1
            return

        if tag == "h1" and self._in_h1:
            self._in_h1 = False

        if tag == "th" and self._in_header_cell:
            self._in_header_cell = False
            self._header_key = self._header_key.strip()
        if tag == "td" and self._in_header_cell:
            self._in_header_cell = False
            self._header_value = self._header_value.strip()
            # 匹配 Author(s) / Written
            if "author" in self._header_key.lower():
                self.author = self._header_value
            elif "written" in self._header_key.lower():
                self.written = self._header_value

        if tag == "table":
            self._in_header_table = False

        if tag == "div" and self._in_publication:
            self._in_publication = False

        if tag == "p" and self._in_p:
            self._in_p = False
            text = self._current_p.strip()
            # 過濾只有換行的空段落
            if text and text != "\n":
                self.body_parts.append(text)

        # inline formatting
        if tag == "i" or tag == "em":
            self._current_p += "*"
        if tag == "b" or tag == "strong":
            self._current_p += "**"

    def handle_data(self, data):
        if self._skip_depth > 0:
            return
        if self._in_h1:
            self.title += data
        if self._in_header_cell:
            if self._in_p:  # 嵌套在 p 內的 th/td
                self._current_p += data
            elif not self._header_key:
                self._header_key = data
            else:
                self._header_value += data
        if self._in_publication:
            self.publication += data
        if self._in_p:
            self._current_p += data

    def handle_startendtag(self, tag, attrs):
        """自閉合標籤：<br/>, <hr/> 等"""
        if tag == "br":
            if self._in_p:
                self._current_p += "\n"

    def handle_starttag_original(self, tag, attrs):
        """保存原始 handle_starttag — 用於 table 檢測"""
        if tag == "table" and ("HeaderTable" in dict(attrs).get("class", "")):
            self._in_header_table = True

    # 重寫以保留 table 檢測
    def unknown_decl(self, data):
        pass


def parse_mecw_html(filepath):
    """解析一個 MECW HTML 檔案，返回 dict"""
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    parser = MECWParser()
    # Monkey-patch: 在 HTMLParser 的 feed 流程中擷取 table class
    # 因為 Python HTMLParser 不支援 class 選擇，改用手動正則預處理
    title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    h1_match = re.search(r'<h1[^>]*class="firstHeading"[^>]*>(.*?)</h1>', html, re.DOTALL)

    # 提取 HeaderTable
    header_match = re.search(
        r'<table class="HeaderTable">(.*?)</table>', html, re.DOTALL
    )

    # 提取 Publication
    pub_match = re.search(
        r'<div class="Publication">(.*?)</div>', html, re.DOTALL
    )

    # 提取主體段落（跳過 head、script、style 等）
    # 簡化策略：提取 <body> 中所有 <p> 標籤內容
    body_start = html.find("<body>")
    body_end = html.find("</body>")
    if body_start == -1:
        body_start = html.find("<body")
    body_html = html[body_start:body_end] if body_start != -1 and body_end != -1 else html

    # 去除 HeaderTable 和 Publication 區塊（避免重複）
    body_html = re.sub(r'<table class="HeaderTable">.*?</table>', '', body_html, flags=re.DOTALL)
    body_html = re.sub(r'<div class="Publication">.*?</div>', '', body_html, flags=re.DOTALL)
    # 去除目錄導航區塊
    body_html = re.sub(r'<div id="GlobalSummary">.*?</div>', '', body_html, flags=re.DOTALL)
    body_html = re.sub(r'<div class="subpagelist">.*?</div>', '', body_html, flags=re.DOTALL)
    body_html = re.sub(r'<div class="mw-references-wrap">.*?</div>', '', body_html, flags=re.DOTALL)
    body_html = re.sub(r'<ol class="references">.*?</ol>', '', body_html, flags=re.DOTALL)

    body_html = re.sub(r'<div class="donotprint".*?</div>', '', body_html, flags=re.DOTALL)
    # 去除 SummaryPage（樞紐頁的導航目錄）
    body_html = re.sub(r'<div id="SummaryPage">.*?</div>', '', body_html, flags=re.DOTALL)

    # 提取 <p> 內容
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', body_html, re.DOTALL)

    # 清理 HTML 標籤的輔助函數
    def clean_html(text):
        # 移除 <a> 標籤但保留文字
        text = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', text)
        # <i> → *
        text = re.sub(r'<i>(.*?)</i>', r'*\1*', text)
        text = re.sub(r'<em>(.*?)</em>', r'*\1*', text)
        # <b> → **
        text = re.sub(r'<b>(.*?)</b>', r'**\1**', text)
        text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text)
        # <br> → 換行
        text = re.sub(r'<br\s*/?>', '\n', text)
        # <sup> → ^
        text = re.sub(r'<sup>(.*?)</sup>', r'^\1', text)
        # <sub> → _
        text = re.sub(r'<sub>(.*?)</sub>', r'_\1', text)
        # 移除其他 HTML 標籤
        text = re.sub(r'<[^>]+>', '', text)
        # 解碼 HTML entities
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
        # 清理多餘空白
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        return text

    # 處理標題
    title = ""
    if h1_match:
        title = clean_html(h1_match.group(1))
    elif title_match:
        title = clean_html(title_match.group(1))

    # 處理元數據
    author = ""
    written = ""
    if header_match:
        header_html = header_match.group(1)
        # 提取 th/td 對
        rows = re.findall(r'<tr>(.*?)</tr>', header_html, re.DOTALL)
        for row in rows:
            ths = re.findall(r'<th>(.*?)</th>', row, re.DOTALL)
            tds = re.findall(r'<td>(.*?)</td>', row, re.DOTALL)
            if ths and tds:
                key = clean_html(ths[0]).lower().strip()
                val = clean_html(tds[0]).strip()
                if 'author' in key:
                    author = val
                elif 'written' in key:
                    written = val

    # 處理 Publication 註記
    publication = ""
    if pub_match:
        publication = clean_html(pub_match.group(1))

    # 處理正文段落
    body_paragraphs = []
    for p in paragraphs:
        cleaned = clean_html(p)
        if cleaned and cleaned != '\n' and len(cleaned) > 1:
            # 跳過來自 publication 的內容（可能已經提取過）
            if publication and cleaned[:30] in publication[:50]:
                continue
            body_paragraphs.append(cleaned)

    body = "\n\n".join(body_paragraphs)

    # 推斷文檔類型
    title_lower = title.lower()
    if not body or len(body) < 20:
        # 樞紐頁或空文檔
        if "content" in title_lower and "volume" in title_lower:
            doc_type = "toc"
        elif any(w in title_lower for w in ["manifesto", "poverty of philosophy", "condition of the working class"]):
            doc_type = "hub"  # 拆分成子頁面的大作品
        else:
            doc_type = "hub"
    elif "letter to" in title_lower or "letter from" in title_lower:
        doc_type = "letter"
    elif any(w in title_lower for w in ["ch.", "chapter", "part ", "section"]):
        doc_type = "chapter"
    elif any(w in title_lower for w in ["preface", "introduction", "foreword", "afterword"]):
        doc_type = "paratext"
    elif author and "progress publishers" in author.lower():
        doc_type = "editorial"
    else:
        doc_type = "article"

    # 推斷年份
    year = None
    if written:
        year_match = re.search(r'(\d{4})', written)
        if year_match:
            year = year_match.group(1)

    return {
        "title": title,
        "author": author,
        "written": written,
        "year": year,
        "publication": publication,
        "doc_type": doc_type,
        "body": body,
    }


def build_frontmatter(doc, volume, file_id):
    """構建 YAML frontmatter 字串"""
    lines = ["---"]
    lines.append(f"id: {file_id}")
    lines.append(f"title: \"{doc['title']}\"")
    lines.append(f"volume: {volume}")
    lines.append(f"doc_type: {doc['doc_type']}")

    if doc["author"]:
        # 標準化作者名
        author = doc["author"]
        if "karl marx" in author.lower() and "friedrich engels" not in author.lower():
            lines.append("author: Karl Marx")
        elif "friedrich engels" in author.lower() and "karl marx" not in author.lower():
            lines.append("author: Friedrich Engels")
        elif "karl marx" in author.lower() and "friedrich engels" in author.lower():
            lines.append("author: Karl Marx & Friedrich Engels")
        else:
            lines.append(f"author: \"{author}\"")

    if doc["written"]:
        lines.append(f"written: \"{doc['written']}\"")
    if doc["year"]:
        lines.append(f"year: {doc['year']}")
    if doc["publication"]:
        # 截取前 200 字符
        pub_short = doc["publication"][:200].replace('"', "'").replace('\n', ' ')
        lines.append(f"publication: \"{pub_short}\"")

    # 狀態（初始為 raw）
    lines.append("status: raw")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def convert_volume(volume, dry_run=False, limit=None):
    """轉換一個 MECW 卷的所有 HTML 檔案"""
    vol_dir = os.path.join(SOURCE_DIR, str(volume))
    if not os.path.isdir(vol_dir):
        print(f"  ✗ Volume {volume} not found at {vol_dir}")
        return 0

    html_files = sorted([
        f for f in os.listdir(vol_dir)
        if f.endswith(".html") and os.path.isfile(os.path.join(vol_dir, f))
    ])

    if limit:
        html_files = html_files[:limit]

    output_vol_dir = os.path.join(OUTPUT_DIR, f"volume-{volume:02d}")
    if not dry_run:
        os.makedirs(output_vol_dir, exist_ok=True)

    success = 0
    for html_file in html_files:
        filepath = os.path.join(vol_dir, html_file)
        try:
            doc = parse_mecw_html(filepath)

            # 生成 ID：MECW{卷}-{編號}
            match = re.match(r'MECW(\d+)-(\d+)\.html', html_file)
            if match:
                file_id = f"MECW{match.group(1)}-{match.group(2)}"
            else:
                file_id = html_file.replace(".html", "")

            frontmatter = build_frontmatter(doc, volume, file_id)
            md_content = frontmatter + doc["body"]

            if not dry_run:
                md_filename = f"{file_id}.md"
                md_path = os.path.join(output_vol_dir, md_filename)
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(md_content)

            success += 1
            if dry_run or success <= 3:
                print(f"  ✓ {html_file} → {file_id}.md  [{doc['doc_type']}]  \"{doc['title'][:60]}...\"")

        except Exception as e:
            print(f"  ✗ {html_file}: {e}")

    if not dry_run:
        print(f"\n  📦 Volume {volume}: {success}/{len(html_files)} converted → {output_vol_dir}")

    return success


# ── CLI ────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MECW HTML → Markdown converter")
    parser.add_argument("--volume", type=str, default="1",
                        help="Volume number or 'all'")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview only, don't write files")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit files per volume")
    args = parser.parse_args()

    if args.volume == "all":
        volumes = sorted([
            int(d) for d in os.listdir(SOURCE_DIR)
            if d.isdigit() and os.path.isdir(os.path.join(SOURCE_DIR, d))
        ])
        total = 0
        for vol in volumes:
            n = convert_volume(vol, dry_run=args.dry_run, limit=args.limit)
            total += n
        print(f"\n✅ Total: {total} documents across {len(volumes)} volumes")
    else:
        convert_volume(int(args.volume), dry_run=args.dry_run, limit=args.limit)
