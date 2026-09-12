import json

PATH = r"d:\_EVAN\Dev\EmotionEngine\append_untranslatable_words.py"

REPLACEMENTS = {
    '"category": "Happiness/Joy"': '"category": "Happiness, Contentment, and Joy"',
    '"category": "Shame/Confusion"': '"category": "Shame and Guilt"',
    '"category": "Fear/Anxiety"': '"category": "Fear and Panic"',
    '"category": "Anger/Boundaries"': '"category": "Anger, Apathy, and Hatred"',
    '"category": "Happiness/Contentment"': '"category": "Happiness, Contentment, and Joy"',
    '"category": "Peace/Solitude"': '"category": "Peace and Solitude"',
    '"category": "Apathy/Depression"': '"category": "Depression and Suicidal Urges"',
    '"category": "Social Comparison"': '"category": "Jealousy and Envy"'
}

def main():
    with open(PATH, encoding="utf-8") as f:
        text = f.read()

    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(text)

    print("Successfully updated categories in append_untranslatable_words.py!")

if __name__ == "__main__":
    main()
