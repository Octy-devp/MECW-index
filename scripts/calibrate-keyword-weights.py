#!/usr/bin/env python3
"""ANOVA 關鍵詞權重校準 — 每個關鍵詞對 tension variance 的貢獻"""
import json, numpy as np
from collections import defaultdict

with open("index/data/keyword-timeseries.json") as f:
    kw_data = json.load(f)["keywords"]
with open("index/data/compiled-documents.json") as f:
    docs = json.load(f)["documents"]

docs_per_year = defaultdict(int)
for d in docs:
    y = d.get("year")
    if y and isinstance(y, int) and 1835 <= y <= 1895:
        docs_per_year[y] += 1

years = sorted({pt["year"] for kw in kw_data.values() for pt in kw})
years = [y for y in years if 1835 <= y <= 1895]

kws = sorted(kw_data.keys())
matrix = np.zeros((len(years), len(kws)))
for j, kw in enumerate(kws):
    kw_series = {d["year"]: d["freq_per_10k"] for d in kw_data.get(kw, [])}
    for i, y in enumerate(years):
        matrix[i, j] = kw_series.get(y, 0)

for i, y in enumerate(years):
    matrix[i] /= max(docs_per_year.get(y, 1), 1)

total_var = np.var(matrix.sum(axis=1))
print("Keyword Variance Contribution (ANOVA-style):")
print(f"{'Keyword':<15} {'Contribution':>12} {'%Var':>8} {'Weight':>8}")
print("-" * 48)

for j, kw in enumerate(kws):
    without = matrix.sum(axis=1) - matrix[:, j]
    contrib = total_var - np.var(without)
    pct = contrib / total_var * 100
    weight = round(pct / 12.5, 2)
    print(f"{kw:<15} {contrib:>12.6f} {pct:>7.1f}% {weight:>8.2f}")

print("\n# Paste into build-theoretical-spectrum.py KEYWORD_WEIGHTS:")
for j, kw in enumerate(kws):
    without = matrix.sum(axis=1) - matrix[:, j]
    pct = (total_var - np.var(without)) / total_var * 100
    weight = round(pct / 12.5, 2)
    print(f'    "{kw}": {weight},')
