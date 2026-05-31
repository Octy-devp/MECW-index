#!/bin/bash
# MECW-index 一鍵部署腳本
# git clone → bash setup.sh → 即可使用

set -e

echo "============================================"
echo "  MECW-index — 兩院制蘇維埃第二院"
echo "  馬克思恩格斯全集結構化索引系統"
echo "============================================"
echo ""

# Python 環境
echo "📦 Checking Python..."
python3 --version || { echo "❌ Python 3 required"; exit 1; }

# 依賴
echo "📦 Installing dependencies..."
pip3 install pyyaml numpy scipy 2>/dev/null || echo "⚠️  Some packages may already be installed"

# 源數據（可選——已有轉換好的 Markdown）
if [ ! -d "../MECW-source" ]; then
    echo ""
    echo "📥 Source data not found. To download MECW HTML source:"
    echo "   git clone --depth 1 https://github.com/MARX-ZH-CN/wikirouge-MECW-2026-Jan-ver.git ../MECW-source"
    echo "   (Skipping — converted Markdown files already included in this repo)"
fi

# 重建 compiled DB
echo ""
echo "🔨 Building compiled database..."
python3 scripts/build-compiled-db.py

# 重建 Prefix
echo "🔨 Building AI Prefix..."
python3 scripts/build-mecw-prefix.py

# 發射多平台 Prefix
echo "🔨 Emitting multi-format prefixes..."
python3 scripts/emit-prefix.py --target all

# 運行驗證
echo ""
echo "✅ Running validation..."
python3 scripts/validate-mecw.py

# 摘要
echo ""
echo "============================================"
echo "  ✅ MECW-index ready!"
echo ""
echo "  Quick start:"
echo "    python3 scripts/query.py --stats"
echo "    python3 scripts/query.py --timeline"
echo "    python3 scripts/query.py --contact 'Ferdinand Lassalle'"
echo ""
echo "  AI analysis (requires DEEPSEEK_API_KEY):"
echo "    python3 scripts/mecw-query-ai.py --dca MECW35-004"
echo "    python3 scripts/mecw-query-ai.py 'Paris Commune' --api"
echo ""
echo "  Spectrum:"
echo "    python3 scripts/build-theoretical-spectrum.py"
echo ""
echo "  Data files:"
echo "    index/data/compiled-documents.json   ($(du -h index/data/compiled-documents.json 2>/dev/null | cut -f1))"
echo "    index/data/character-network.json    ($(du -h index/data/character-network.json 2>/dev/null | cut -f1))"
echo "    index/data/theoretical-spectrum.json ($(du -h index/data/theoretical-spectrum.json 2>/dev/null | cut -f1))"
echo "============================================"
