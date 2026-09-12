import json

PATH = r"d:\_EVAN\Dev\EmotionEngine\emotions.json"

CATEGORY_MAP = {
    # Old/Sloppy/Specific -> Canonical
    "Happiness/Joy": "Happiness, Contentment, and Joy",
    "Happiness/Contentment": "Happiness, Contentment, and Joy",
    "Peace/Solitude": "Peace and Solitude",
    "Bittersweet peace": "Peace and Solitude",
    "Fear/Anxiety": "Fear and Panic",
    "Shame/Confusion": "Shame and Guilt",
    "Anger/Boundaries": "Anger, Apathy, and Hatred",
    "Apathy/Depression": "Depression and Suicidal Urges",
    "Social Comparison": "Jealousy and Envy"
}

def main():
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)

    changed = 0
    for o in data:
        cat = o.get("category")
        if cat in CATEGORY_MAP:
            o["category"] = CATEGORY_MAP[cat]
            changed += 1

    print(f"Normalized {changed} records in emotions.json.")

    # Verify counts
    from collections import Counter
    counts = Counter(x["category"] for x in data)
    print("\nCanonical Category Counts:")
    for cat, count in sorted(counts.items()):
        print(f"  {cat}: {count}")

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

if __name__ == "__main__":
    main()
