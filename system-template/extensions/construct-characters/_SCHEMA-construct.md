# 漣漪角色系統（Construct Characters）— Schema 定義

> **所屬擴展**：`system-template/extensions/construct-characters/`  
> **版本**：v1.0  
> **日期**：2026-05-30  
> **用途**：定義「理應存在但故事未深入」的推導角色——從已知角色出發，透過漣漪搜索法推導缺席者  
> **設計原則**：construct 角色不與已確立角色混淆。所有 construct 角色標記 `inferred: true`，`status: construct`，`source: ripple`

---

## 〇、為什麼需要 Construct Characters？

傳統角色索引只收錄**已出場**的角色。但任何敘事世界都存在「缺席的應然存在者」——他們沒有場景文本可引用，但從歷史邏輯、制度結構、家族關係中可以推導出他們的存在。

例如：
- 威廉二世必然有皇太子（Kronprinz Wilhelm），但 ECC 未寫入
- MI5 創始總監 Vernon Kell 必然有副手和核心團隊
- 聖恩救濟院必然有其他孤兒和修女

這些角色不是「憑空發明」——他們是**漣漪**：已知角色是投入歷史池塘的石頭，漣漪圈出那些理應存在的人。

---

## 一、漣漪層級定義

| 層級 | 名稱 | 推導邏輯 | 置信度 | 例子 |
|:---:|------|---------|:---:|------|
| **R1** | 血緣漣漪 | 家族/血緣關係必然存在 | ≥0.90 | 威廉二世 → 皇太子 |
| **R2** | 制度漣漪 | 官職/機構必然有同僚和下屬 | ≥0.80 | Vernon Kell → MI5 副手 |
| **R3** | 歷史漣漪 | 同時期歷史中對應的人物 | ≥0.70 | 德皇有太子 → 沙皇的其他大公 |
| **R4** | 敘事漣漪 | 故事邏輯需要但未寫入 | ≥0.50 | Leo 在伊頓的老師/同學 |

---

## 二、Construct Character Schema

```yaml
id: kronprinz-wilhelm              # 唯一 ID（與 character-mappings 格式一致）
name: 威廉皇太子                    # 中文名
name_en: Kronprinz Wilhelm          # 英文名
status: construct                   # construct | confirmed（若後續被文本確認）
ripple_source: wilhelm-ii           # 漣漪來源角色
ripple_layer: R1                    # R1 | R2 | R3 | R4
ripple_rationale: >                 # 推導理由
  威廉二世（1859-1941）與奧古斯塔·維多利亞皇后育有七名子女。
  長子威廉皇太子（1882-1951）在真實歷史中是皇位繼承人，
  在一戰期間擔任第五軍團司令。在 ECC 的替代歷史中，
  他作為皇室成員理應存在於柏林宮廷場景中。
confidence: 0.95                    # 推導置信度（0-1）
historical_basis: true              # 是否有真實歷史人物對應
ecc_role: antagonist                # 在 ECC 中的敘事角色（若已知）
related_characters:                 # 與已確立角色的關係
  - character: wilhelm-ii
    relation: father
  - character: prince-eitel
    relation: brother
appears_in: []                      # 若後續被加入場景，記錄場景 ID
```

---

## 三、與既有體系的關係

| 體系 | 關係 |
|------|------|
| `index/characters/*.md` | construct 角色**不寫入**角色視圖，除非後續被場景文本確認 |
| `.taskbook/mappings/character-mappings.yaml` | construct 角色有**獨立映射檔**：`construct-characters.yaml` |
| `index/data/compiled-scenes.json` | construct 角色不出現在 `character_ids` 中（沒有場景文本） |
| Extra Stage 群組 | construct 角色可被**標記**為群組的缺失成員 |
| DCA 知識庫 | 若 construct 角色有真實歷史對應，可在知識庫中創建條目 |

---

## 四、漣漪搜索算法（偽代碼）

```python
def ripple_search(known_character, max_layers=4):
    """
    從已知角色出發，逐層搜索漣漪角色。
    """
    results = []
    
    # R1: 血緣漣漪
    if has_family(known_character):
        for member in get_family_members(known_character):
            if not in_character_index(member):
                results.append(ConstructChar(member, layer='R1', confidence=0.90))
    
    # R2: 制度漣漪
    for institution in get_institutions(known_character):
        for role in get_institutional_roles(institution):
            if not in_character_index(role):
                results.append(ConstructChar(role, layer='R2', confidence=0.80))
    
    # R3: 歷史漣漪（對應人物）
    for counterpart in get_historical_counterparts(known_character):
        if not in_character_index(counterpart):
            results.append(ConstructChar(counterpart, layer='R3', confidence=0.70))
    
    # R4: 敘事漣漪
    for logical_role in get_narrative_gaps(known_character):
        if not in_character_index(logical_role):
            results.append(ConstructChar(logical_role, layer='R4', confidence=0.50))
    
    return results
```

---

## 五、驗證規則

| 規則 | 說明 |
|------|------|
| **不與已確立角色重疊** | construct 角色的 ID 不得出現在 `character-mappings.yaml` 中 |
| **必須有漣漪來源** | 每個 construct 角色必須標註 `ripple_source` |
| **置信度分級** | R1≥0.90, R2≥0.80, R3≥0.70, R4≥0.50 |
| **歷史人物校驗** | 若 `historical_basis: true`，需確認真實歷史中確實存在此人 |
| **升級路徑** | 若 construct 角色後續出現在場景文本中，升級為 `status: confirmed`，移入 `character-mappings.yaml` |
