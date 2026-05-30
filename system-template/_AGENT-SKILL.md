# [SYSTEM-NAME] Agent Skill

> Agent 操作 [SYSTEM-NAME] 的工作流指南。

## Activation Triggers
- User asks to validate [SYSTEM-NAME] entries
- User asks to query or search [SYSTEM-NAME]
- User asks to audit [SYSTEM-NAME] quality

## Golden Paths

```bash
# 查詢
python scripts/_query.py search "關鍵詞"    # 全文搜索
python scripts/_query.py list --cat cat-a   # 按分類
python scripts/_query.py stats              # 統計概覽
python scripts/_query.py gap                # 覆蓋缺口

# 編譯
python scripts/_build-compiled-db.py        # 重建 compiled JSON
python scripts/_build-prefix.py             # 重建 AI Prefix

# 驗證
python scripts/_validate-schema.py          # Frontmatter 格式校驗
```

## Hard Constraints
1. **SSOT**: `_SCHEMA.md` 是格式規範的唯一真實來源
2. **不修改原始條目**: 驗證腳本僅檢查，不自動修改
3. **編譯後再查詢**: 每次新增/修改條目後必須重建 compiled DB
