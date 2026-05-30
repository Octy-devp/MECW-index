#!/usr/bin/env python3
"""
MECW AI Prefix 生成器 v0.2 — Version B (DCA 實例嵌入版)
與 Version A 的差異：嵌入 2 篇完整 DCA 提取實例（而不是抽象定義）

用法：
  python scripts/build-mecw-prefix-v2.py
"""

import json, os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
COMPILED = ROOT / "index" / "data" / "compiled-documents.json"
NETWORK = ROOT / "index" / "data" / "character-network.json"
PREFIX_OUT = ROOT / "index" / "data" / "mecw-prefix-v2.txt"

def build():
    with open(COMPILED, "r") as f:
        data = json.load(f)
    with open(NETWORK, "r") as f:
        network = json.load(f)

    meta = data["_meta"]
    contacts = network["contacts"]

    lines = []
    lines.append("=" * 60)
    lines.append("MECW DCA Extraction System v0.2 — WORKED-EXAMPLE EMBEDDED")
    lines.append("Task: Extract Crisis-Delay-Alternative-Direction from Marx/Engels texts")
    lines.append("Method: DO NOT invent DCA. EXTRACT the structure Marx already uses.")
    lines.append("=" * 60)

    # ── WORKED EXAMPLE 1: Gotha Critique ──────────────
    lines.append("")
    lines.append("## WORKED EXAMPLE 1: Critique of the Gotha Programme (Marx, 1875)")
    lines.append("")
    lines.append("This is how Marx does Crisis-Delay-Alternative-Direction analysis.")
    lines.append("Study this example carefully. All your extractions must follow this pattern.")
    lines.append("")
    lines.append("### TEXT (abridged):")
    lines.append('"Labor is not the source of all wealth. Nature is just as much the source')
    lines.append('of use values... A socialist program cannot allow such bourgeois phrases')
    lines.append('to pass over in silence the conditions that alone give them meaning."')
    lines.append('')
    lines.append('"What we have to deal with here is a communist society, not as it has')
    lines.append('developed on its own foundations, but on the contrary, just as it emerges')
    lines.append('from capitalist society; which is thus in every respect still stamped')
    lines.append('with the birthmarks of the old society from whose womb it emerges."')
    lines.append('')
    lines.append('"Between capitalist and communist society there lies the period of the')
    lines.append('revolutionary transformation of the one into the other. Corresponding to')
    lines.append('this is also a political transition period in which the state can be')
    lines.append('nothing but the revolutionary dictatorship of the proletariat."')
    lines.append('')
    lines.append('"In a higher phase of communist society... after labor has become not')
    lines.append('only a means of life but life\'s prime want; after the productive forces')
    lines.append('have also increased... only then can the narrow horizon of bourgeois')
    lines.append('right be crossed in its entirety and society inscribe on its banners:')
    lines.append('From each according to his ability, to each according to his needs!"')
    lines.append("")
    lines.append("### DCA EXTRACTION FROM THIS TEXT:")
    lines.append("```yaml")
    lines.append("crisis_diagnosis:")
    lines.append("  type: organizational_degeneration")
    lines.append("  specific: |")
    lines.append("    The 1875 merger of the Eisenach and Lassallean parties produced a")
    lines.append("    draft program that replaced scientific socialism with Lassallean")
    lines.append("    slogans: 'iron law of wages', 'undiminished proceeds of labor',")
    lines.append("    'free state', 'reactionary mass'. Marx diagnoses this not as")
    lines.append("    bad wording but as PRINCIPLED RETREAT — the theoretical gains")
    lines.append("    of Capital and the International are being traded away for")
    lines.append("    organizational unity.")
    lines.append("  evidence: [\"What a crime it is to attempt to force on our Party again,")
    lines.append("             as dogmas, ideas which in a certain period had some meaning")
    lines.append("             but have now become obsolete verbal rubbish\"]")
    lines.append("")
    lines.append("lag_mechanism:")
    lines.append("  layers: [theoretical, organizational, ideological]")
    lines.append("  theoretical: |")
    lines.append("    Lassalle himself did not know what wages were — he took the")
    lines.append("    appearance (value of labor) for the essence (value of labor-power).")
    lines.append("    Fifteen years after Capital Vol.1, the party program reverts to")
    lines.append("    pre-scientific economics.")
    lines.append("  organizational: |")
    lines.append("    Merger pressure: the Eisenach wing accepted theoretical concessions")
    lines.append("    to secure unification. Organization was prioritized over clarity.")
    lines.append("  ideological: |")
    lines.append("    The program's 'servile belief in the state' — treating the Prussian")
    lines.append("    state as a neutral instrument rather than an organ of class rule.")
    lines.append("")
    lines.append("alternative_proposal:")
    lines.append("  method: systematic_correction")
    lines.append("  elements:")
    lines.append("    - Replace 'iron law of wages' with scientific theory of labor-power")
    lines.append("    - Replace 'free state' with 'revolutionary dictatorship of proletariat'")
    lines.append("    - Replace 'fair distribution' with two-phase analysis:")
    lines.append("      Phase 1: 'to each according to labor' (still bourgeois right)")
    lines.append("      Phase 2: 'to each according to needs' (post-scarcity)")
    lines.append("    - Replace national framework with internationalism")
    lines.append("")
    lines.append("direction_constraint:")
    lines.append("  core: productive_forces_determine_distribution_possibilities")
    lines.append("  specific: |")
    lines.append("    Phase 1 communism is 'still stamped with the birthmarks of the old")
    lines.append("    society.' Equal right remains bourgeois right because it measures")
    lines.append("    with the standard of labor, ignoring individual inequality. Only")
    lines.append("    when productive forces are fully developed and labor becomes")
    lines.append("    'life's prime want' can distribution transcend bourgeois right.")
    lines.append("  key_insight: \"Right can never be higher than the economic structure")
    lines.append("                of society and its cultural development conditioned thereby.\"")
    lines.append("```")
    lines.append("")

    # ── WORKED EXAMPLE 2: Communist Manifesto Ch.1 ─────
    lines.append("## WORKED EXAMPLE 2: Manifesto of the Communist Party, Ch.1 (Marx & Engels, 1848)")
    lines.append("")
    lines.append("### TEXT (abridged — opening paragraphs):")
    lines.append('"The history of all hitherto existing society is the history of class struggles."')
    lines.append('')
    lines.append('"The modern bourgeois society that has sprouted from the ruins of feudal')
    lines.append('society has not done away with class antagonisms. It has but established')
    lines.append('new classes, new conditions of oppression, new forms of struggle in place')
    lines.append('of the old ones."')
    lines.append('')
    lines.append('"Modern industry has established the world market... The bourgeoisie...')
    lines.append('has played a most revolutionary part. Wherever it has got the upper hand,')
    lines.append('it has put an end to all feudal, patriarchal, idyllic relations... It has')
    lines.append('drowned the most heavenly ecstasies of religious fervor... in the icy water')
    lines.append('of egotistical calculation."')
    lines.append('')
    lines.append('"A spectre is haunting Europe — the spectre of communism."')
    lines.append("")
    lines.append("### DCA EXTRACTION FROM THIS TEXT:")
    lines.append("```yaml")
    lines.append("crisis_diagnosis:")
    lines.append("  type: revolutionary_conjuncture")
    lines.append("  specific: |")
    lines.append("    Europe 1848: feudal relations have been shattered by bourgeois")
    lines.append("    revolution, but the bourgeoisie has immediately created its own")
    lines.append("    antagonist — the proletariat. The crisis is not just political")
    lines.append("    but STRUCTURAL: the same productive forces that destroyed feudalism")
    lines.append("    now threaten bourgeois property itself. Periodic commercial crises")
    lines.append("    ('epidemics of over-production') expose the contradiction between")
    lines.append("    socialized production and private appropriation.")
    lines.append("")
    lines.append("lag_mechanism:")
    lines.append("  layers: [organizational, ideological]")
    lines.append("  organizational: |")
    lines.append("    Workers compete against each other, not yet conscious of their")
    lines.append("    class interest. 'The organization of the proletarians into a class,")
    lines.append("    and consequently into a political party, is continually being upset")
    lines.append("    again by the competition between the workers themselves.'")
    lines.append("  ideological: |")
    lines.append("    Bourgeois ideology (freedom = free trade, equality = juridical")
    lines.append("    equality) masks exploitation. Existing socialist literature")
    lines.append("    (feudal, petty-bourgeois, 'true' socialism) reflects backward")
    lines.append("    class positions and misdirects worker consciousness.")
    lines.append("")
    lines.append("alternative_proposal:")
    lines.append("  method: revolutionary_political_program")
    lines.append("  elements:")
    lines.append("    - Abolition of bourgeois private property")
    lines.append("    - Proletariat organized as ruling class → democratic conquest")
    lines.append("    - Ten transitional measures (progressive taxation, abolition of")
    lines.append("      inheritance, centralization of credit and transport, etc.)")
    lines.append("    - Ultimate goal: classless society where 'the free development of")
    lines.append("      each is the condition for the free development of all'")
    lines.append("")
    lines.append("direction_constraint:")
    lines.append("  core: national_specificity_of_transitional_measures")
    lines.append("  specific: |")
    lines.append("    'These measures will of course be different in different countries.'")
    lines.append("    The communist program is not a universal blueprint but must be")
    lines.append("    adapted to each country's level of capitalist development, class")
    lines.append("    composition, and political conditions. The transition presupposes")
    lines.append("    that capitalism has already developed the productive forces to a")
    lines.append("    level where scarcity is socially produced, not natural.")
    lines.append("```")
    lines.append("")

    # ── TASK INSTRUCTION ────────────────────────────
    lines.append("## YOUR TASK")
    lines.append("")
    lines.append("You will receive a Marx or Engels text. Your job is to EXTRACT")
    lines.append("(not invent) the DCA structure — exactly as demonstrated above.")
    lines.append("")
    lines.append("CRITICAL RULES:")
    lines.append("1. CRISIS must be historically specific — name the actual event, conjuncture,")
    lines.append("   or structural contradiction the text responds to. NOT generic labels.")
    lines.append("2. LAG must identify MECHANISMS (not just 'X is behind'). What specifically")
    lines.append("   prevents the resolution? Is it organizational, theoretical, ideological,")
    lines.append("   or material? Multiple layers may operate simultaneously.")
    lines.append("3. ALTERNATIVE must be the text's actual proposal, not what you think Marx")
    lines.append("   should have said. Quote the text when possible.")
    lines.append("4. DIRECTION must identify the MATERIAL CONSTRAINTS that limit the")
    lines.append("   alternative — not what 'ought' to happen, but what conditions enable")
    lines.append("   or constrain the direction proposed.")
    lines.append("5. Use the same YAML structure as the worked examples. Every field must")
    lines.append("   contain concrete historical content, not abstract phrases.")
    lines.append("6. If the text does NOT contain all four DCA dimensions, mark missing")
    lines.append("   dimensions as null and explain why (e.g., 'letter - no alternative')")
    lines.append("")

    # ── QUICK REFERENCE ─────────────────────────────
    lines.append("## QUICK REFERENCE")
    lines.append(f"- MECW covers 1818–2004, core Marx/Engels period 1835–1895")
    lines.append(f"- {meta['total_documents']} documents in 50 volumes")
    lines.append(f"- Peak years: 1848 (revolutions), 1871 (Paris Commune)")
    lines.append(f"- 694 correspondents, Marx↔Engels: 1,545 letters")
    lines.append("")
    lines.append("Key periods for DCA extraction:")
    lines.append("  1840s: Revolutionary upheaval → Communist Manifesto")
    lines.append("  1850s: Counter-revolution, exile journalism, 1857 crisis")
    lines.append("  1860s: Capital Vol.1, First International")
    lines.append("  1870s: Paris Commune, Gotha Programme, Anti-Dühring")
    lines.append("  1880s-90s: Engels' late syntheses, Second International")
    lines.append("")

    prefix = "\n".join(lines)

    os.makedirs(PREFIX_OUT.parent, exist_ok=True)
    with open(PREFIX_OUT, "w", encoding="utf-8") as f:
        f.write(prefix)

    stats = {
        "version": "v0.2",
        "characters": len(prefix),
        "words": len(prefix.split()),
        "lines": len(lines),
        "worked_examples": 2,
        "file": str(PREFIX_OUT),
    }
    print(f"✅ {PREFIX_OUT}")
    print(f"   {stats['words']} words, {stats['lines']} lines")
    print(f"   2 worked examples embedded")
    return stats

if __name__ == "__main__":
    build()
