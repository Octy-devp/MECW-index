# MECW-index 總綱計劃書

> **版本**：v0.1  
> **日期**：2026-05-30  
> **願景**：將 Marx/Engels Collected Works 50 卷轉化為可導航、可交叉引用、可進行 DCA 深度分析的結構化文獻資料庫  
> **架構**：兩院制蘇維埃第二院——與 ECC 平行自治

---

## 階段總覽

```
Phase 0: 源數據獲取         ──→ ✅ HTML clone (230MB)
Phase 1: HTML→MD 轉換       ──→ ✅ 6,759 篇 Markdown
Phase 2: 基礎索引            ──→ 🔄 compiled-documents.json ✅
Phase 3: 人物/地點索引        ──→ ⬜
Phase 4: DCA 知識庫          ──→ ⬜ （核心價值）
Phase 5: 交叉引用網絡         ──→ ⬜
Phase 6: 頻譜分析            ──→ ⬜ （theoretical_tension 長波）
Phase 7: 查詢/API            ──→ ⬜
```

---

## 當前狀態

| 指標 | 數值 |
|------|:---:|
| 文獻總數 | 6,759 |
| 有年份 | 6,425 (95.1%) |
| 核心時期 (1835–1895) | 6,367 |
| 編譯資料庫 | 3.6 MB JSON |
| Git 倉庫 | https://github.com/Octy-devp/MECW-index |

---

## 下一步

1. **人物索引**：從 4,306 封信中提取通信對象，建立 Marx/Engels 的人物網絡
2. **DCA 試點**：選 5 篇關鍵文獻（《共產黨宣言》《哥達綱領批判》《法蘭西內戰》等）進行 DCA 深度分析
3. **與 ECC 交叉**：建立 `CROSS-CHAMBER.md` 協調委員會
