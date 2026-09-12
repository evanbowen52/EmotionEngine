"""Enrich emotions.json with Jungian archetypes and psychological deities."""
import json
import os
import unicodedata

JSON_PATH = r"d:\_EVAN\Dev\EmotionEngine\emotions.json"

JUNGIAN_ARCHETYPES = [
    {
        "term": "The Self",
        "origin": "Jungian Psychology (Archetype)",
        "category": "Peace and Solitude",
        "intensity": "Intense",
        "energy": "Low",
        "pleasantness": "Very High",
        "is_archetype": True,
        "description": "The archetype of wholeness and the organizing, unifying center of the entire psyche (both conscious and unconscious), slowly realized through the lifelong journey of individuation.",
        "connections": []
    },
    {
        "term": "The Shadow",
        "origin": "Jungian Psychology (Archetype)",
        "category": "Shame and Guilt",
        "intensity": "Intense",
        "energy": "High",
        "pleasantness": "Low",
        "is_archetype": True,
        "description": "The unconscious aspect of the personality containing repressed drives, unacknowledged feelings, instincts, and creative potentials which the conscious ego rejects or fails to identify in itself.",
        "connections": [
            {
                "term": "The Self",
                "relation": "leads_to",
                "notes": "Integrating and acknowledging the Shadow is the foundational, brave first milestone of realizing the Self."
            },
            {
                "term": "Shame",
                "relation": "adjacent",
                "notes": "Parts of the personality are cast into the Shadow because the ego experiences them as sources of moral shame."
            }
        ]
    },
    {
        "term": "Anima / Animus",
        "origin": "Jungian Psychology (Archetype)",
        "category": "Social Connection",
        "intensity": "Medium",
        "energy": "Medium",
        "pleasantness": "Neutral (Bittersweet)",
        "is_archetype": True,
        "description": "The inner feminine archetype in the male psyche (Anima), or the inner masculine archetype in the female psyche (Animus); the deep contrasexual psychological bridge to the unconscious mind and the soul.",
        "connections": [
            {
                "term": "The Self",
                "relation": "leads_to",
                "notes": "Integrating the inner contrasexual archetype is a major milestone in psychological individuation."
            }
        ]
    },
    {
        "term": "Persona",
        "origin": "Jungian Psychology (Archetype)",
        "category": "Social Connection",
        "intensity": "Soft",
        "energy": "Medium",
        "pleasantness": "Neutral",
        "is_archetype": True,
        "description": "The social mask or facade we present to society; designed to conform to cultural expectations, protect the vulnerable ego, and mediate our interaction with the external world.",
        "connections": [
            {
                "term": "Fitting In",
                "relation": "adjacent",
                "notes": "The Persona is the psychological structure we construct to adapt and fit into our peer groups."
            }
        ]
    }
]

DEITY_ARCHETYPES = {
    "Poseidôn (Ποσειδῶν)": {
        "description": "Used in archetypal and Jungian psychology to represent the Poseidon archetype—the raw, instinctual surge of the deep subconscious, raw emotional power, and the tranquil, boundless 'oceanic feeling' of merging with the infinite universe.",
        "is_archetype": True,
        "category": "Peace and Solitude",
        "connections": [
            {
                "term": "The Self",
                "relation": "adjacent",
                "notes": "Savoring the deep calm of the oceanic feeling aligns with realizing Self-wholeness."
            }
        ]
    },
    "Apollo (Ἀπόλλων)": {
        "description": "Used in Jungian psychology to represent the Apollo archetype—the emotional and cognitive drive for order, rationality, conscious clarity, logical structure, and harmonic calm; the drive to rise above emotional chaos.",
        "is_archetype": True,
        "category": "Peace and Solitude",
        "connections": [
            {
                "term": "The Self",
                "relation": "leads_to",
                "notes": "Apollo's focus on logic and clarity can help structure the journey toward self-understanding."
            }
        ]
    },
    "Diónysos (Διόνυσος)": {
        "description": "Used in depth psychology to represent the Dionysus archetype—the emotional state of ecstatic ego-dissolution, raw physical celebration, somatic joy, boundary-breaking release, and sensory merging with the collective.",
        "is_archetype": True,
        "category": "Happiness, Contentment, and Joy"
    },
    "Háidēs (Άͅδης)": {
        "description": "Used in depth psychology to represent the Hades archetype—the emotional state of deep solitary introspection, quiet soul-work, and descending into the 'underworld' of the subconscious to process shadow-work, grief, and silent transformation.",
        "is_archetype": True,
        "category": "Sadness and Grief",
        "connections": [
            {
                "term": "The Shadow",
                "relation": "adjacent",
                "notes": "Hades represents the active psychological presence of working directly with shadow elements in the subconscious."
            }
        ]
    },
    "Afrodíti (Αφροδίτη)": {
        "description": "Used in archetypal psychology to represent the Aphrodite archetype—the numinous, passionate drive for creative connection, aesthetic attraction, erotic love, and the deep, soul-stirring appreciation of beauty.",
        "is_archetype": True,
        "category": "Social Connection"
    },
    "Zeus (Ζεύς)": {
        "description": "Used in archetypal psychology to represent the Zeus archetype—the psychological drive for sovereignty, supreme authority, focused ambition, executive power, and the creation of clean, protective boundaries.",
        "is_archetype": True,
        "category": "Anger, Apathy, and Hatred"
    },
    "Gaia (Γαῖα)": {
        "description": "Used in depth psychology to represent the Earth Mother archetype—the instinct for unconditional nurturing, emotional grounding, primary security, and a physical, comforting connection to natural systems.",
        "is_archetype": True,
        "category": "Peace and Solitude"
    },
    "Dēmētēr (Δημήτηρ)": {
        "description": "Used in Jungian psychology to represent the Maternal archetype—the profound emotional drive to care, nurture, and protect, coupled with the agonizing grief, depression, and sense of loss triggered by separation.",
        "is_archetype": True,
        "category": "Sadness and Grief"
    },
    "Persephónē (Περσεφόνη)": {
        "description": "Used in depth psychology to represent the Persephone archetype—the psychological transition from youth and passivity to queen of the underworld, bridging the conscious ego world and the deep subconscious.",
        "is_archetype": True,
        "category": "Confusion"
    },
    "Mnemosyne (Μνημοσύνη)": {
        "description": "Used in depth psychology to represent the archetype of Memory and Reminiscence—the deep emotional connection to the past, retrieval of ancestral wisdom, and the poetic integration of life's narrative.",
        "is_archetype": True,
        "category": "Peace and Solitude"
    },
    "Nemesis (Νέμεσις)": {
        "description": "Used in psychology to represent the Nemesis archetype—the emotional experience of ultimate accountability, and the painful but necessary leveling of hubris and pride.",
        "is_archetype": True,
        "category": "Shame and Guilt"
    }
}

def key(t):
    return unicodedata.normalize("NFC", t.strip()).casefold()

def main():
    with open(JSON_PATH, encoding="utf-8") as f:
        db = json.load(f)

    # Index existing terms
    by_key = {key(e["term"]): i for i, e in enumerate(db) if isinstance(e, dict) and "term" in e}

    # 1. Merge core Jungian Archetypes
    print("Merging core Jungian Archetypes...")
    added = 0
    updated = 0
    for ja in JUNGIAN_ARCHETYPES:
        k = key(ja["term"])
        if k in by_key:
            idx = by_key[k]
            db[idx].update(ja)
            updated += 1
        else:
            db.append(ja)
            by_key[k] = len(db) - 1
            added += 1

    print(f"Core Jungian: {added} added, {updated} updated.")

    # 2. Enrich existing mythological deities
    print("Enriching existing deities with depth-psychology archetypal dimensions...")
    enriched_count = 0
    for term, data in DEITY_ARCHETYPES.items():
        k = key(term)
        if k in by_key:
            idx = by_key[k]
            # Update description, category, and is_archetype tag
            db[idx]["description"] = data["description"]
            db[idx]["is_archetype"] = True
            db[idx]["category"] = data["category"]
            if "connections" in data:
                db[idx]["connections"] = data["connections"]
            
            # Change origin to include "Archetype" for clarity
            orig = db[idx].get("origin", "Greek")
            if "archetype" not in orig.lower():
                db[idx]["origin"] = f"{orig} (Archetypal Metaphor)"
            
            enriched_count += 1
        else:
            # Let's search if the term exists under a slightly different name (e.g. without the greek letters)
            normalized_search = key(term.split('(')[0].strip())
            found = False
            for db_term_key, db_idx in by_key.items():
                if normalized_search in db_term_key:
                    db[db_idx]["description"] = data["description"]
                    db[db_idx]["is_archetype"] = True
                    db[db_idx]["category"] = data["category"]
                    if "connections" in data:
                        db[db_idx]["connections"] = data["connections"]
                    orig = db[db_idx].get("origin", "Greek")
                    db[db_idx]["origin"] = f"{orig} (Archetypal Metaphor)"
                    enriched_count += 1
                    found = True
                    break
            if not found:
                print(f"Warning: deity term '{term}' not found in database.")

    print(f"Enriched {enriched_count} mythological deities in the dataset.")

    # Write back to emotions.json
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Successfully updated emotions.json with Jungian expansion! Total entries: {len(db)}")

if __name__ == "__main__":
    main()

