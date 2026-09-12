"""Unify Atlas of the Heart relationships and Positive Lexicography ingestion into emotions.json."""
import json
import subprocess
import os
import sys
import unicodedata

JSON_PATH = r"d:\_EVAN\Dev\EmotionEngine\emotions.json"

# 1. Atlas of the Heart Terms to Inject
ATLAS_EMOTIONS = [
    {
        "term": "Stress",
        "origin": "English",
        "category": "Anxiety",
        "intensity": "Medium",
        "energy": "High",
        "pleasantness": "Low",
        "description": "A state of mental or emotional strain resulting from demanding circumstances; feeling 'in the weeds' but trying to cope.",
        "connections": [
            {
                "term": "Overwhelmed",
                "relation": "leads_to",
                "notes": "Stress can boil over into overwhelm when cognitive capacity is fully blown out."
            }
        ]
    },
    {
        "term": "Overwhelmed",
        "origin": "English",
        "category": "Anxiety",
        "intensity": "Intense",
        "energy": "Low",
        "pleasantness": "Low",
        "description": "Extreme cognitive and emotional saturation where functioning is temporarily frozen or shut down; being 'blown out of the water'.",
        "connections": [
            {
                "term": "Stress",
                "relation": "triggered_by",
                "notes": "Overwhelm is often triggered by accumulated, unmanaged stress."
            }
        ]
    },
    {
        "term": "Empathy",
        "origin": "English",
        "category": "Social Connection",
        "intensity": "Medium",
        "energy": "Medium",
        "pleasantness": "High",
        "description": "The ability to understand and share the feelings of another; connecting with the vulnerability that underpins their experience.",
        "connections": [
            {
                "term": "Sympathy",
                "relation": "confused_with",
                "notes": "Sympathy feels 'for' someone (creating distance), while empathy feels 'with' someone (creating connection)."
            },
            {
                "term": "Compassion",
                "relation": "leads_to",
                "notes": "Empathic connection is the cognitive and emotional precursor to compassionate action."
            }
        ]
    },
    {
        "term": "Sympathy",
        "origin": "English",
        "category": "Social Connection",
        "intensity": "Soft",
        "energy": "Low",
        "pleasantness": "Neutral",
        "description": "Feelings of pity and sorrow for someone else's misfortune; feeling 'for' them, which can create polite distance rather than connection.",
        "connections": [
            {
                "term": "Empathy",
                "relation": "confused_with",
                "notes": "Sympathy keeps us on the bank of the river looking down at someone; empathy requires us to climb down into the river with them."
            }
        ]
    },
    {
        "term": "Compassion",
        "origin": "English",
        "category": "Social Connection",
        "intensity": "Medium",
        "energy": "Medium",
        "pleasantness": "High",
        "description": "A deep awareness of and sympathy for another's suffering, coupled with the desire and active intent to alleviate it.",
        "connections": [
            {
                "term": "Empathy",
                "relation": "triggered_by",
                "notes": "Compassion is triggered and informed by our ability to empathize with the suffering of others."
            }
        ]
    },
    {
        "term": "Regret",
        "origin": "English",
        "category": "Sadness and Grief",
        "intensity": "Medium",
        "energy": "Low",
        "pleasantness": "Low",
        "description": "A feeling of sadness or disappointment over something that has happened or been done, especially when accompanied by personal accountability.",
        "connections": [
            {
                "term": "Disappointment",
                "relation": "confused_with",
                "notes": "Regret involves personal agency/accountability; disappointment is when the outcome is outside of your control."
            }
        ]
    },
    {
        "term": "Disappointment",
        "origin": "English",
        "category": "Sadness and Grief",
        "intensity": "Medium",
        "energy": "Low",
        "pleasantness": "Low",
        "description": "Sadness or displeasure caused by the nonfulfillment of one's hopes or expectations; typically feels outside of personal control.",
        "connections": [
            {
                "term": "Regret",
                "relation": "confused_with",
                "notes": "Disappointment is when we feel let down by external expectations; regret is when we feel let down by our own choices."
            }
        ]
    },
    {
        "term": "Shame",
        "origin": "English",
        "category": "Shame and Guilt",
        "intensity": "Intense",
        "energy": "Low",
        "pleasantness": "Very Low",
        "description": "The deeply painful feeling or experience of believing that we are flawed and therefore unworthy of love and belonging ('I am bad').",
        "connections": [
            {
                "term": "Guilt",
                "relation": "confused_with",
                "notes": "Shame focuses on who we are ('I am bad'); guilt focuses on what we have done ('I did something bad')."
            }
        ]
    },
    {
        "term": "Guilt",
        "origin": "English",
        "category": "Shame and Guilt",
        "intensity": "Medium",
        "energy": "Medium",
        "pleasantness": "Low",
        "description": "The painful feeling of cognitive dissonance resulting from holding our behavior against our values ('I did something bad').",
        "connections": [
            {
                "term": "Shame",
                "relation": "confused_with",
                "notes": "Guilt is adaptive and helpful for moral course-correction; shame is destructive and correlated with disconnection."
            }
        ]
    },
    {
        "term": "Hubris",
        "origin": "English",
        "category": "Shame and Guilt",
        "intensity": "Intense",
        "energy": "High",
        "pleasantness": "Low",
        "description": "Exaggerated pride or self-confidence; an ego-centric grandiosity that masks deep-seated insecurity and leads to social disconnection.",
        "connections": [
            {
                "term": "Pride",
                "relation": "confused_with",
                "notes": "Hubris is ego-focused ('I am great') and creates disconnection; pride is effort-focused ('I did a great thing') and is socially bonding."
            }
        ]
    },
    {
        "term": "Pride",
        "origin": "English",
        "category": "Happiness, Contentment, and Joy",
        "intensity": "Medium",
        "energy": "Medium",
        "pleasantness": "High",
        "description": "A feeling of deep pleasure or satisfaction derived from one's own achievements or efforts; constructive self-respect.",
        "connections": [
            {
                "term": "Hubris",
                "relation": "confused_with",
                "notes": "Authentic pride is grounded in humility and connection; hubris is an inflated ego state that rejects feedback."
            }
        ]
    },
    {
        "term": "Belonging",
        "origin": "English",
        "category": "Social Connection",
        "intensity": "Medium",
        "energy": "Low",
        "pleasantness": "Very High",
        "description": "The innate human desire to be part of something larger; being accepted and valued for our authentic self without needing to change.",
        "connections": [
            {
                "term": "Fitting In",
                "relation": "opposite_of",
                "notes": "Belonging is being accepted for who you are; fitting in is changing who you are to be accepted."
            }
        ]
    },
    {
        "term": "Fitting In",
        "origin": "English",
        "category": "Social Connection",
        "intensity": "Soft",
        "energy": "Medium",
        "pleasantness": "Neutral",
        "description": "Assessing a situation and acclimating or changing who we are in order to be accepted, which actually acts as a barrier to true belonging.",
        "connections": [
            {
                "term": "Belonging",
                "relation": "opposite_of",
                "notes": "Fitting in is a major barrier to belonging, as it trades away authenticity for temporary peer safety."
            }
        ]
    },
    {
        "term": "Freudenfreude",
        "origin": "German",
        "category": "Happiness, Contentment, and Joy",
        "intensity": "Medium",
        "energy": "Medium",
        "pleasantness": "High",
        "description": "The German term for finding vicarious joy and pleasure in other people's success and happiness; the opposite of Schadenfreude.",
        "connections": [
            {
                "term": "Schadenfreude",
                "relation": "opposite_of",
                "notes": "Freudenfreude celebrates and strengthens relationships through shared joy; Schadenfreude takes pleasure in another's suffering."
            }
        ]
    }
]

# We also want to update Schadenfreude's connections so it links back to Freudenfreude
SCHADENFREUDE_CONNECTIONS = [
    {
        "term": "Freudenfreude",
        "relation": "opposite_of",
        "notes": "Schadenfreude is taking joy in another's misery; Freudenfreude is taking joy in another's success."
    }
]

# 2. Positive Lexicography Mapping Rules
THEME_MAP = {
    "love": "Social Connection",
    "relationship": "Social Connection",
    "communication/interaction": "Social Connection",
    "tradition": "Social Connection",
    "revelry": "Happiness, Contentment, and Joy",
    "excitement/intensity": "Happiness, Contentment, and Joy",
    "savoring/appreciation": "Happiness, Contentment, and Joy",
    "peace/calm": "Peace and Solitude",
    "aesthetics": "Peace and Solitude",
    "relationship with nature/place": "Peace and Solitude",
    "reality/god": "Peace and Solitude",
    "grit": "Happiness, Contentment, and Joy",
    "skill": "Happiness, Contentment, and Joy",
    "morality": "Shame and Guilt",
    "understanding/perception": "Confusion"
}

def key(t):
    return unicodedata.normalize("NFC", t.strip()).casefold()

def fetch_lexicography_raw():
    print("Fetching Positive Lexicography data via temporary Node.js script...")
    js_file = "temp_lex_fetch.js"
    js_code = """
const https = require('https');
https.get('https://hifisamurai.github.io/lexicography/data~app~v2.973c00c1ead08a4d3b9e.js', (res) => {
  let data = '';
  res.on('data', c => data += c);
  res.on('end', () => {
    const s = data.indexOf('e.exports=[');
    if (s === -1) {
      console.error('not found');
      process.exit(1);
    }
    const arrStart = s + 'e.exports='.length;
    const nextMod = data.indexOf('56:function');
    if (nextMod === -1) {
      console.error('not found 56:function');
      process.exit(1);
    }
    const arrEnd = data.lastIndexOf(']', nextMod) + 1;
    const arr = eval(data.substring(arrStart, arrEnd));
    console.log(JSON.stringify(arr));
  });
}).on('error', (err) => {
  console.error(err);
  process.exit(1);
});
"""
    with open(js_file, "w", encoding="utf-8") as f:
        f.write(js_code)

    try:
        res = subprocess.run(["node", js_file], capture_output=True, text=True, check=True, encoding="utf-8")
        raw_json = res.stdout.strip()
        data = json.loads(raw_json)
        print(f"Successfully fetched and parsed {len(data)} terms from Positive Lexicography Project!")
        return data
    finally:
        if os.path.exists(js_file):
            os.remove(js_file)

def main():
    # Load existing database
    with open(JSON_PATH, encoding="utf-8") as f:
        db = json.load(f)

    # Index existing terms
    by_key = {key(e["term"]): i for i, e in enumerate(db) if isinstance(e, dict) and "term" in e}

    # 1. Merge Atlas of the Heart Emotions
    print("Merging Atlas of the Heart terms and relationships...")
    atlas_added = 0
    atlas_updated = 0
    for ae in ATLAS_EMOTIONS:
        k = key(ae["term"])
        if k in by_key:
            # Update existing node with connections, description, and details
            idx = by_key[k]
            db[idx]["connections"] = ae["connections"]
            db[idx]["description"] = ae["description"]
            db[idx]["category"] = ae["category"]
            db[idx]["intensity"] = ae["intensity"]
            db[idx]["energy"] = ae["energy"]
            db[idx]["pleasantness"] = ae["pleasantness"]
            atlas_updated += 1
        else:
            # Append as new node
            db.append(ae)
            by_key[k] = len(db) - 1
            atlas_added += 1

    # Connect Schadenfreude explicitly
    sk = key("Schadenfreude")
    if sk in by_key:
        db[by_key[sk]]["connections"] = SCHADENFREUDE_CONNECTIONS
        print("Linked Schadenfreude to Freudenfreude.")

    print(f"Atlas of the Heart complete: {atlas_added} added, {atlas_updated} updated.")

    # 2. Ingest Positive Lexicography Terms
    lex_raw = fetch_lexicography_raw()
    lex_added = 0
    for item in lex_raw:
        term_name = item.get("name", "").strip()
        if not term_name:
            continue
        
        # Check for duplicates (e.g. Toska, Mamihlapinatapei may already be present!)
        k = key(term_name)
        if k in by_key:
            continue

        # Map theme
        raw_theme = item.get("theme", {}).get("name", "")
        category = THEME_MAP.get(raw_theme, "Nonspecific")

        # Set default values based on themes for nice spatial separation in polar map
        intensity = "Medium"
        energy = "Medium"
        pleasantness = "High"

        if raw_theme in ["peace/calm", "aesthetics", "relationship with nature/place"]:
            energy = "Low"
        elif raw_theme in ["excitement/intensity", "revelry"]:
            energy = "High"
            intensity = "Intense"
        
        if raw_theme == "negative":
            pleasantness = "Low"

        origin_name = item.get("origin", {}).get("name", "Unknown").strip()
        # Clean up spanish typo from the raw lexicography website data
        if origin_name.lower() == "spansih":
            origin_name = "Spanish"
        else:
            origin_name = origin_name.title()

        new_entry = {
            "term": term_name,
            "origin": origin_name,
            "category": category,
            "intensity": intensity,
            "energy": energy,
            "pleasantness": pleasantness,
            "description": item.get("description", "")
        }

        db.append(new_entry)
        by_key[k] = len(db) - 1
        lex_added += 1

    print(f"Positive Lexicography complete: Added {lex_added} brand new terms.")

    # Save expanded database
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Successfully wrote {len(db)} total emotional terms back to emotions.json!")

if __name__ == "__main__":
    main()

