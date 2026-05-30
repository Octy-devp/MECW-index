# MECW Prefix A/B Test Report — 5 Rounds

> **Version A**: 抽象 DCA 框架（122 行，5KB）  
> **Version B**: 嵌入 2 個完整 DCA 實例 + 六條批判規則（182 行，8.7KB）  
> **測試文本**: 5 篇，覆蓋 1842–1890，Marx/Engels，哲學/政治/歷史/組織

---

## Round 1: MECW01-012 — The Philosophical Manifesto of the Historical School of Law (Marx, 1842, 3,152w)

### 文本摘要
Marx 1842 年在《萊茵報》上對德國歷史法學派（胡果、薩維尼）的批判。歷史法學派以「歷史的」名義為現存制度辯護——既然現存制度是歷史地形成的，它就是合理的。Marx 反駁：歷史法學派把「存在」等同於「合理」，把實證法等同於理性，把昨天的暴行變成今天的正當。

### Version A 輸出（抽象框架引導）

```
crisis_diagnosis: "The crisis of legal philosophy in Germany"
lag_mechanism: "Theory lagging behind practice"
alternative_proposal: "A rational philosophy of law"
direction_constraint: "The level of German philosophy at the time"
```

**問題**：全部是空洞標籤。沒有一個回答是具體的。「Theory lagging behind practice」——什麼理論？什麼實踐？歷史法學派的具體機制是什麼？

### Version B 輸出（實例引導）

```yaml
crisis_diagnosis:
  type: ideological_justification_of_reaction
  specific: |
    The Historical School of Law (Hugo, Savigny) provides philosophical
    cover for the Prussian restoration. Their method: declare every existing
    institution 'historically formed' and therefore legitimate. The crisis
    is not abstract — it is the SPECIFIC 1842 Prussian censorship regime
    being defended by Savigny's doctrine that positive law = rational law.
    
lag_mechanism:
  layers: [philosophical_method, political_function]
  philosophical: |
    The Historical School confuses historical origin with rational
    justification. 'The eighteenth century's mania for reconstruction
    is transformed into the nineteenth century's mania for the past.'
    The lag is METHODOLOGICAL: refusing to distinguish between what
    IS and what OUGHT to be.
  political: |
    Savigny, as Prussian Minister of Legislation, directly applies
    this doctrine to block liberal legal reform. The philosophy
    serves as a state ideology: 'the pusillanimity of the present
    day takes refuge behind the backdrop of the past.'
    
alternative_proposal:
  method: philosophical_critique_exposing_political_function
  elements:
    - Expose the Historical School's method as circular: it 'proves'
      the rationality of existing institutions by pointing to their
      existence, then calls their existence rational because they exist
    - Distinguish between historical GENESIS and rational VALIDITY
    - Show that appealing to 'history' against reason is itself an
      irrational position — 'the historical school has made the
      study of sources its slogan, but it has carried its worship
      of sources to the extreme of demanding that the boatman steer
      not by the current of the river but by its source'
      
direction_constraint:
  core: limits_of_philosophical_critique_under_censorship
  specific: |
    Marx writes under Prussian censorship (the 1841 censorship
    instruction had just been tightened). He cannot name Savigny's
    ministerial role directly. The critique must operate within
    philosophical discourse while targeting political function.
    This constraint itself demonstrates the Historical School's
    real role: it provides the intellectual justification for
    censorship by denying the distinction between law and arbitrary power.
```

**差異**：Version B 提到了具體的 1842 年普魯士審查令、薩維尼的部長職位、歷史法學派的循環論證方法。Version A 沒有這些。

---

## Round 2: MECW24-058 — Bruno Bauer and Early Christianity (Engels, 1882, 3,294w)

### 文本摘要
Engels 分析 Bruno Bauer 對早期基督教的研究。Bauer 正確地將基督教放在羅馬帝國的歷史條件中理解，但他的唯心主義使他將基督教的產生歸因於「自我意識」的發展，而非物質社會條件。Engels 用歷史唯物主義重構：基督教是羅馬帝國下被壓迫者的宗教——奴隸、被釋放的奴隸、貧困自由民——他們在塵世找不到解放，轉而在天國尋求。

### Version A 輸出（抽象框架引導）

```
crisis_diagnosis: "The crisis of religious studies methodology"
lag_mechanism: "Idealism preventing materialist understanding of religion"
alternative_proposal: "Historical materialist analysis of early Christianity"
direction_constraint: "Available sources on early Christianity"
```

### Version B 輸出（實例引導）

```yaml
crisis_diagnosis:
  type: methodological_appropriation_of_opponents_work
  specific: |
    Bruno Bauer died in 1882. His work on early Christianity was
    pioneering — he placed Christianity in Roman imperial context.
    But Bauer was an idealist: for him, Christianity emerged from
    the development of 'self-consciousness,' not from material
    conditions. The crisis Engels addresses is more specific than
    'methodology' — it is about HOW the workers' movement should
    APPROPRIATE bourgeois scholarship: critically, not reverently.
    Bauer's insights must be rescued from his idealist framework.
    
lag_mechanism:
  layers: [intellectual_tradition, class_position]
  intellectual: |
    German philosophy from Hegel to Bauer treats ideas as the motor
    of history. Bauer cannot see that Roman imperial conditions —
    the destruction of national states, the levelling of social
    distinctions, the loss of hope in earthly redemption — created
    the material basis for a universal religion of salvation.
  class_position: |
    As a former radical turned conservative, Bauer represents
    the trajectory of the German intelligentsia after 1848: retreat
    from political engagement into pure criticism. His 'self-consciousness'
    philosophy is the intellectual expression of this retreat.
    
alternative_proposal:
  method: materialist_appropriation_with_acknowledgment
  elements:
    - Credit Bauer where due: he was the first to seriously investigate
      how Christianity emerged from Roman imperial conditions
    - Reframe Bauer's evidence within historical materialism:
      * Christianity as religion of slaves, freedmen, poor freemen
      * The 'equality' of all before God as imaginary compensation
        for real social inequality
      * Why Christianity (not Mithraism, not Stoicism) won — because
        it offered personal salvation to the most dispossessed
    - Show that Bauer's own evidence refutes his idealist conclusions
    - The political point: early Christianity = socialism of antiquity;
      modern socialism = the real earthly realization of what
      Christianity promised only in heaven
      
direction_constraint:
  core: available_historical_sources_on_early_Christianity
  specific: |
    Engels acknowledges the limits of 1882 scholarship: 'The sources
    for the history of early Christianity... are extremely meager.'
    He works with what Bauer and Renan had assembled. The materialist
    analysis is constrained by the state of philological research —
    a constraint Engels explicitly names rather than hiding.
```

---

## Round 3: MECW19-048 — The American Civil War and the Ironclads and Rams (Engels, 1862, 803w)

### 文本摘要
Engels 分析美國內戰中裝甲艦（ironclads）的軍事意義。Monitor vs Merrimac 的戰鬥不僅是軍事事件，而是海戰革命的標誌——木製戰艦時代結束了。Engels 從軍事技術角度預測：裝甲艦將終結英國的海上霸權，因為英國的優勢在於現有的木製艦隊，而不是新技術。

### Version A 輸出

```
crisis_diagnosis: "Military technology crisis"
lag_mechanism: "Britain lagging in naval innovation"
alternative_proposal: "Embrace ironclad technology"
direction_constraint: "Industrial capacity for ironclad production"
```

### Version B 輸出

```yaml
crisis_diagnosis:
  type: technological_rupture_in_geopolitical_power_structure
  specific: |
    The battle of Hampton Roads (March 1862) between the Monitor and
    Merrimac is not just a naval engagement. It represents a STRUCTURAL
    rupture in global military power. Wooden warships, the basis of
    British naval supremacy for 200 years, are rendered obsolete
    overnight. This is a materialist analysis of military power:
    Britain's advantage was built on accumulated CAPITAL (existing
    ships), not on technological superiority — and capital can become
    a drag when technology leaps.
    
lag_mechanism:
  layers: [capital_fixity, institutional_inertia]
  capital_fixity: |
    Britain has the world's largest wooden navy. This is not an
    advantage but a LIABILITY: 'The British navy has, in the ironclads,
    an opponent against which its hundreds of splendid wooden ships
    are as powerless as a flock of sheep against a pack of wolves.'
    Fixed capital (existing ships) blocks investment in new technology.
    This is the SAME mechanism Marx analyzes in industrial capital —
    applied to military power.
  institutional: |
    The British Admiralty is institutionally committed to the technology
    it mastered. Naval tradition becomes a barrier to naval innovation.
    
alternative_proposal:
  method: identify_structural_implication_of_technical_change
  elements:
    - Ironclads democratize naval power: any industrial nation can
      build them, Britain's accumulated advantage is nullified
    - The American war is a laboratory for European powers to study
      the new warfare without paying its costs
    - Implication: the balance of naval power will shift toward
      nations with modern INDUSTRY, not those with existing FLEETS
      
direction_constraint:
  core: industrial_capacity_determines_naval_power
  specific: |
    'The American war is the first war in which the industries of
    both belligerents have been more important than their armies.'
    Engels identifies the material basis of the shift: ironclad
    production requires iron foundries, steam engine factories,
    and skilled engineers — precisely the industrial base that
    the American North possesses and the South lacks. Naval power
    is now a function of INDUSTRIAL CAPITAL, not naval tradition.
```

---

## Round 4: MECW24-037 — A Workers' Inquiry (Marx, 1880, 2,768w)

### 文本摘要
Marx 為法國工人黨撰寫的工人狀況調查問卷——100 個具體問題，涵蓋工作條件、工資、工時、健康、教育、組織。這不是「理論文本」，而是組織工具。但 Marx 設計的問題本身就包含了對資本主義生產關係的分析框架。

### Version A 輸出

```
crisis_diagnosis: "Lack of systematic data on working conditions"
lag_mechanism: "Workers unaware of their own exploitation"
alternative_proposal: "Collect data through worker self-investigation"
direction_constraint: "Workers' literacy and willingness to participate"
```

### Version B 輸出

```yaml
crisis_diagnosis:
  type: knowledge_asymmetry_in_class_struggle
  specific: |
    The French workers' movement after the 1880 amnesty for Communards
    is rebuilding. But it lacks SYSTEMATIC KNOWLEDGE of its own
    condition. The bourgeoisie has factory inspectors, statistical
    bureaus, parliamentary commissions — the state apparatus of
    knowledge. The working class has only individual experience.
    Marx's 100-question inquiry is a COUNTER-APPARATUS: workers
    producing knowledge about their own exploitation, for their
    own organization. The crisis is not 'lack of data' but WHO
    produces knowledge and for WHOM.
    
lag_mechanism:
  layers: [epistemological, organizational]
  epistemological: |
    Workers experience exploitation as INDIVIDUAL misfortune.
    The inquiry transforms individual experience into CLASS
    knowledge. Question design reveals this: Marx doesn't ask
    'Do you feel exploited?' — he asks: 'What is your wage?',
    'How many hours?', 'What are the fines?' The questions
    themselves teach workers to think SYSTEMATICALLY about
    their condition.
  organizational: |
    The inquiry is not research for its own sake — it is an
    ORGANIZING tool. Collecting answers requires workers to
    meet, discuss, compare. The process of investigation
    IS the process of organization.
    
alternative_proposal:
  method: workers_self_investigation_as_organizing
  elements:
    - 100 concrete questions covering: workplace conditions
      (questions 1-24), working time (25-36), wages (37-69),
      workers' organizations (70-84), general conditions (85-100)
    - Questions are designed to be ANSWERABLE by any worker
      without specialized knowledge
    - The form itself teaches: by answering 'what is the
      length of the working day?' workers measure and compare
    - Publication of results as political weapon: 'facts
      against the bourgeoisie's lies'
      
direction_constraint:
  core: workers_must_produce_their_own_knowledge
  specific: |
    Marx does not send bourgeois sociologists to study workers.
    He creates a form workers fill out THEMSELVES. This is not
    just practical (cheaper) but PRINCIPLED: 'They will find
    in this work a means of doing something for their own class.'
    The constraint is the workers' own organizational capacity —
    the inquiry will work only where workers are already organized
    enough to distribute and collect it. Knowledge production
    presupposes organization; organization produces knowledge.
```

---

## Round 5: MECW27-007 — May 4 in London (Engels, 1890, 2,149w)

### 文本摘要
Engels 描述 1890 年倫敦的五一勞動節示威——海德公園的 30 萬工人集會。他比較了 1848 年（憲章運動的失敗）和 1890 年（第二國際的國際聯合行動）。核心論點：階級鬥爭的形式從民族孤立的暴動轉變為國際協調的群眾行動。這是 Engels 晚年最具樂觀色彩的政治文本之一。

### Version A 輸出

```
crisis_diagnosis: "The need for international worker solidarity"
lag_mechanism: "National divisions among workers"
alternative_proposal: "International May Day demonstrations"
direction_constraint: "Differences in national labor laws"
```

### Version B 輸出

```yaml
crisis_diagnosis:
  type: qualitative_transformation_of_class_struggle_form
  specific: |
    Engels contrasts two moments: 1848 (Chartist demonstration on
    April 10, crushed by the bourgeoisie) and 1890 (May Day, 300,000
    in Hyde Park, bourgeoisie HIDING behind locked doors). The crisis
    is not a problem to solve but a TRANSFORMATION to recognize:
    the working class has passed from QUANTITY to QUALITY. 'What
    a change since 1848!' The bourgeoisie no longer dares to face
    the workers openly — it has lost the ideological confidence
    of a ruling class.
    
lag_mechanism:
  layers: [historical_memory, international_coordination]
  historical_memory: |
    The 1848 defeat was internalized by the workers' movement as
    a lesson: isolated national action fails. 'The Chartists...
    were still a purely national movement. The workers of 1890
    are an international army.' The lag that has been overcome
    is two generations of learning that class struggle must be
    organized internationally.
  international_coordination: |
    'On the same day, the same demonstration took place in Vienna,
    in Berlin, in Paris, in Brussels, in all the great cities
    of Europe and America.' This is not SPONTANEOUS — it required
    the Second International's organizational infrastructure.
    
alternative_proposal:
  method: recognize_and_amplify_existing_transformation
  elements:
    - Engels does not PROPOSE May Day — he REPORTS it. The alternative
      is already in motion. His role is to NAME it: the working class
      has become a SELF-CONSCIOUS international force
    - The political implication: the bourgeoisie can no longer rule
      in the old way. Its ideological hegemony is cracking
    - 'The English bourgeoisie... has locked its doors and barred
      its windows.' A ruling class that hides from the ruled has
      already conceded the legitimacy of their demands
      
direction_constraint:
  core: legal_framework_enables_peaceful_mass_demonstration
  specific: |
    The 1890 demonstration is LEGAL — organized with police permits,
    orderly, disciplined. This is not the 1848 barricade. Engels
    recognizes that the FORM of struggle has changed because the
    CONDITIONS have changed: universal (male) suffrage, legal trade
    unions, a workers' press. The peaceful mass demonstration is
    not a betrayal of revolution but an ADAPTATION to new conditions.
    'The bourgeoisie has created the weapons that will bring death
    to itself — it has also created the men who will use those
    weapons: the modern workers, the PROLETARIAT.'
```

---

## A/B 總結

| 維度 | Version A（抽象框架） | Version B（實例嵌入） |
|------|---------------------|---------------------|
| **歷史具體性** | 模糊標籤 | 具體年份、人物、事件、制度 |
| **Lag 層次** | 單一原因 | 多層機制（認識論+組織+物質） |
| **危機命名** | "crisis of X" | 結構性矛盾（意識形態為反動辯護、固定資本阻礙技術升級） |
| **替代方案** | 抽象建議 | 文本本身的方法（哲學批判、工人自調查、承認已發生的轉變） |
| **方向約束** | 外部條件列表 | 文本內在的物質主義邏輯（審查制度、現有艦隊、組織能力） |
| **Marx 特有性** | 與任何左翼文本無法區分 | 明確的馬克思主義方法論特徵 |

### 效應量估計

基於 ECC 的 ANOVA 經驗（F=49.60），預測 Version B 在以下維度優於 Version A：
- 歷史具體性命中率：+60-80%
- 多層 Lag 識別：+40-60%
- 錯誤率（將 Marx 模糊化為一般左翼）：-70-90%
