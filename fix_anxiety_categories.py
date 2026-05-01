"""Fix miscategorized 'Anxiety' rows in emotions.json (DEI vocabulary alignment)."""
import json
from collections import defaultdict

PATH = r"d:\_EVAN\Dev\EmotionEngine\emotions.json"

# From Emotional-Vocabulary-List.pdf (DEI)
ANXIETY = {
    "Soft": {
        "Capable",
        "Clear-headed",
        "Focused",
        "Organized",
        "Prepared",
    },
    "Medium": {
        "Activated",
        "Anxious",
        "Attentive",
        "Competent",
        "Conscientious",
        "Deadline-Conscious",
        "Efficient",
        "Energized",
        "Excited",
        "Forward-Focused",
        "Motivated",
        "Nervous",
        "Ready",
        "Task-Focused",
        "Vigilant",
        "Worried",
    },
    "Intense": {
        "Accomplished",
        "Driven",
        "Frenzied",
        "Hyper-Activated",
        "Laser-Focused",
        "Pressed",
        "Vigorous",
    },
}

FEAR = {
    "Soft": {
        "Alert",
        "Apprehensive",
        "Aware",
        "Careful",
        "Cautious",
        "Clear",
        "Concerned",
        "Conscious",
        "Curious",
        "Disconcerted",
        "Disquieted",
        "Edgy",
        "Fidgety",
        "Hesitant",
        "Insecure",
        "Instinctive",
        "Intuitive",
        "Leery",
        "Lucid",
        "Mindful",
        "Oriented",
        "Pensive",
        "Perceptive",
        "Shy",
        "Timid",
        "Uneasy",
        "Watchful",
    },
    "Medium": {
        "Afraid",
        "Alarmed",
        "Attentive",
        "Aversive",
        "Distrustful",
        "Disturbed",
        "Fearful",
        "Focused",
        "Jumpy",
        "Perturbed",
        "Rattled",
        "Ready",
        "Resourceful",
        "Safety-Seeking",
        "Shaky",
        "Startled",
        "Suspicious",
        "Unnerved",
        "Unsettled",
        "Vigorous",
        "Wary",
    },
    "Intense": {
        "Dissociated",
        "Filled with Dread",
        "Frenzied",
        "Healing from Trauma",
        "Horrified",
        "Hyper-Activated",
        "Immobile",
        "Laser-Focused",
        "Motionless",
        "Panicked",
        "Paralyzed",
        "Petrified",
        "Phobic",
        "Reintegrated",
        "Self-Preserving",
        "Shocked",
        "Survival-Focused",
        "Terrorized",
        "Violent",
    },
}

JEALOUSY = {
    "Soft": {
        "Concerned",
        "Connected",
        "Disbelieving",
        "Fair",
        "Insecure",
        "Inspired",
        "Protective",
        "Self-Aware",
        "Trusting",
        "Vulnerable",
        "Wanting",
    },
    "Medium": {
        "Ambitious",
        "Amorous",
        "Bonded",
        "Committed",
        "Covetous",
        "Demanding",
        "Desirous",
        "Devoted",
        "Disrespected",
        "Distrustful",
        "Driven",
        "Envious",
        "Equitable",
        "Generous",
        "Guarded",
        "Jealous",
        "Just",
        "Lonely",
        "Loving",
        "Loyal",
        "Motivated",
        "Prosperous",
        "Romantic",
        "Secure",
        "Self-Preserving",
        "Threatened",
        "Wary",
    },
    "Intense": {
        "Affluent",
        "Ardent",
        "Avaricious",
        "Fixated",
        "Deprived",
        "Gluttonous",
        "Grasping",
        "Greedy",
        "Green with Envy",
        "Longing",
        "Lustful",
        "Obsessed",
        "Passionate",
        "Persistently Jealous",
        "Possessive",
        "Power-Hungry",
        "Resentful",
        "Voracious",
    },
}

HAPPINESS = {
    "Soft": {
        "Amused",
        "Calm",
        "Comfortable",
        "Encouraged",
        "Engaged",
        "Friendly",
        "Hopeful",
        "Inspired",
        "Jovial",
        "Naïve",
        "Open",
        "Peaceful",
        "Smiling",
        "Unaware",
        "Upbeat",
    },
    "Medium": {
        "Appreciative",
        "Cheerful",
        "Confident",
        "Contented",
        "Delighted",
        "Excited",
        "Fulfilled",
        "Glad",
        "Gleeful",
        "Gratified",
        "Happy",
        "Healthy Self-Esteem",
        "Invigorated",
        "Joyful",
        "Lively",
        "Merry",
        "Optimistic",
        "Playful",
        "Pleased",
        "Praiseworthy",
        "Proud",
        "Rejuvenated",
        "Tickled",
        "Unrealistic",
        "Ungrounded",
    },
    "Intense": {
        "Arrogant",
        "Awe-Filled",
        "Blissful",
        "Ecstatic",
        "Egocentric",
        "Elated",
        "Enthralled",
        "Euphoric",
        "Exhilarated",
        "Expansive",
        "Flighty",
        "Giddy",
        "Gullible",
        "Heedless",
        "Inflated",
        "Jubilant",
        "Manic",
        "Oblivious",
        "Overconfident",
        "Overjoyed",
        "Radiant",
        "Rapturous",
        "Reckless",
        "Renewed",
        "Satisfied",
        "Self-Aggrandized",
        "Thrilled",
    },
}

SADNESS = {
    "Soft": {
        "Contemplative",
        "Disappointed",
        "Disconnected",
        "Fluid",
        "Grounded",
        "Listless",
        "Low",
        "Steady",
        "Regretful",
        "Relaxed",
        "Releasing",
        "Restful",
        "Wistful",
    },
    "Medium": {
        "Dejected",
        "Discouraged",
        "Dispirited",
        "Down",
        "Drained",
        "Grieving",
        "Heavy-hearted",
        "Honoring",
        "Lamenting",
        "Melancholy",
        "Mournful",
        "Rejuvenated",
        "Relieved",
        "Remembering",
        "Respectful",
        "Restored",
        "Sad",
        "Soothed",
        "Sorrowful",
        "Still",
        "Weepy",
    },
    "Intense": {
        "Anguished",
        "Bereaved",
        "Cleansed",
        "Despairing",
        "Despondent",
        "Forlorn",
        "Grief-Stricken",
        "Heartbroken",
        "Inconsolable",
        "Morose",
        "Released",
        "Revitalized",
        "Sanctified",
    },
}

DEPRESSION = {
    "Soft": {
        "Apathetic",
        "Discouraged",
        "Disinterested",
        "Dispirited",
        "Downtrodden",
        "Fed Up",
        "Feeling Worthless",
        "Flat",
        "Helpless",
        "Humorless",
        "Impulsive",
        "Indifferent",
        "Isolated",
        "Lethargic",
        "Listless",
        "Pessimistic",
        "Practical",
        "Purposeless",
        "Realistic",
        "Resolute",
        "Tired",
        "Withdrawn",
        "World-Weary",
    },
    "Medium": {
        "Bereft",
        "Certain",
        "Constantly Irritated, Angry, or Enraged (see the Anger list above)",
        "Crushed",
        "Depressed",
        "Desolate",
        "Desperate",
        "Drained",
        "Emancipated",
        "Empty",
        "Fatalistic",
        "Gloomy",
        "Hibernating",
        "Hopeless",
        "Immobile",
        "Inactive",
        "Inward-Focused",
        "Joyless",
        "Miserable",
        "Morbid",
        "Overwhelmed",
        "Passionless",
        "Pleasureless",
        "Sullen",
    },
    "Intense": {
        "Agonized",
        "Anguished",
        "Bleak",
        "Death-Seeking",
        "Devastated",
        "Doomed",
        "Freed",
        "Frozen",
        "Gutted",
        "Liberated",
        "Nihilistic",
        "Numbed",
        "Reborn",
        "Reckless",
        "Self-Destructive",
        "Suicidal",
        "Tormented",
        "Tortured",
        "Transformed",
    },
}

CAT_NAMES = {
    "fear": "Fear and Panic",
    "jealousy": "Jealousy and Envy",
    "happiness": "Happiness, Contentment, and Joy",
    "sadness": "Sadness and Grief",
    "depression": "Depression and Suicidal Urges",
}

MAPS = [
    ("fear", FEAR),
    ("jealousy", JEALOUSY),
    ("happiness", HAPPINESS),
    ("sadness", SADNESS),
    ("depression", DEPRESSION),
]


def candidates_for(term: str, intensity: str) -> list[tuple[str, str]]:
    """Return [(key, category_name), ...] in stable PDF order."""
    if intensity not in ("Soft", "Medium", "Intense"):
        return []
    t = term.strip()
    out: list[tuple[str, str]] = []
    for key, m in MAPS:
        if t in m.get(intensity, set()):
            out.append((key, CAT_NAMES[key]))
    return out


def main() -> None:
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)

    counts: dict[tuple[str, str, str], int] = defaultdict(int)
    for o in data:
        counts[(o["term"].strip(), o["intensity"], o["category"])] += 1

    fixed = 0
    for o in data:
        if o.get("category") != "Anxiety":
            continue
        term = o["term"].strip()
        intens = o["intensity"]
        if intens not in ("Soft", "Medium", "Intense"):
            continue
        if term in ANXIETY.get(intens, set()):
            continue

        cands = candidates_for(term, intens)
        if not cands:
            continue

        chosen = None
        for _key, cat in cands:
            k = (term, intens, cat)
            if counts[k] == 0:
                chosen = cat
                break
        if chosen is None:
            chosen = cands[0][1]

        counts[(term, intens, "Anxiety")] -= 1
        counts[(term, intens, chosen)] += 1
        o["category"] = chosen
        fixed += 1

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("Reassigned from Anxiety:", fixed)


if __name__ == "__main__":
    main()
