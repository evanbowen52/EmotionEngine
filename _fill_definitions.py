"""Fill placeholder descriptions using NLTK WordNet, then dictionaryapi.dev for gaps."""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from nltk.corpus import wordnet as wn

JSON_PATH = r"d:\_EVAN\Dev\EmotionEngine\emotions.json"
UA = "EmotionEngine/1.0 (local; definitions sync)"
API_DELAY = 0.55

_EMOTION_BOOST = re.compile(
    r"feel|feeling|emotion|mood|unhappy|unhapp|happy|distress|distressed|angry|sad|sorrow|"
    r"worry|worri|mental|psychological|anguish|agitat|upset|pain\b|griev|"
    r"fear|anxi|panic|shame|guilt|jealous|envy|confus|depress|grief|irrit|"
    r"disgust|hostil|rage|calm|peace|joy|content|euphor|elat|bliss|longing|"
    r"nostalg|bitter|apathetic|letharg|listless|detach|numb|resent|spite|"
    r"contempt|mourn|bereav|forlorn|despond|glum|sullen|morose|"
    r"wistful|pensive|peniten|remorse|embarrass|humiliat|awkward|"
    r"vulnerab|timid|shy|cautious|alert|instinct|panic|terror|horror|"
    r"euphor|manic|jovial|merry|cheer|bliss|awe|radiant|thrill|"
    r"irritable|crank|peeved|annoy|frustrat|furi|rage|ire|wrath|"
    r"loath|hatred|hostile|spite|veng|bitter|indignant|offend|",
    re.I,
)
_IRRELEVANT = re.compile(
    r"\b(cricket|wickets|automobile|merchandise|champagne|brandy|batsman|"
    r"geomagnet|electric|stress mark|accent|phonetic)\b",
    re.I,
)

_OVERRIDES: dict[str, str] = {
    "laser-focused": "Extremely concentrated in attention or effort; mentally locked onto a single goal or detail.",
    "self-preserving": "Acting to protect oneself from harm or loss; oriented toward safety and survival.",
    "deadline-conscious": "Acutely aware of time limits and due dates, often with elevated urgency.",
    "task-focused": "Directing attention primarily toward completing a specific task or duty.",
    "forward-focused": "Oriented toward the future rather than the past; anticipating what comes next.",
    "safety-seeking": "Actively looking for security, protection, or conditions that reduce risk.",
    "survival-focused": "Prioritizing immediate survival needs and threat avoidance above other concerns.",
    "healing from trauma": "In a process of recovering emotionally or psychologically after deep distress or injury.",
    "healthy self-esteem": "A stable, realistic positive regard for oneself without excessive arrogance.",
    "self-aggrandized": "Characterized by an inflated view of one's own importance or abilities.",
    "self-effacing": "Tending to downplay oneself modestly, sometimes minimizing one's own needs or visibility.",
    "self-respecting": "Showing regard for one's own dignity, boundaries, and worth.",
    "self-aware": "Conscious of one's own feelings, motives, and patterns.",
    "self-assured": "Confident in one's own abilities and judgments.",
    "self-condemning": "Harshly judging or blaming oneself.",
    "self-conscious": "Uncomfortably aware of oneself as seen by others; socially inhibited or embarrassed.",
    "self-flagellating": "Punishing or blaming oneself severely, often in a habitual way.",
    "well-boundaried": "Maintaining clear personal limits; able to protect one's space and priorities.",
    "clear-eyed": "Seeing situations without illusion; emotionally honest about what is true.",
    "clouded": "(Of thought or judgment) unclear, confused, or obscured.",
    "soft-focused": "Gentle or diffuse attention rather than sharp concentration; slightly vague in perception.",
    "filled with dread": "Dominated by a strong sense of looming fear or doom.",
    "green with envy": "Consumed by envy; visibly jealous of another's advantage.",
    "persistently jealous": "Experiencing jealousy that continues over time rather than as a brief spike.",
    "constantly irritated, angry, or enraged (see the anger list above)": "A chronic or recurring pattern of irritation or anger (see the anger vocabulary for related states).",
    "hyper-activated": "In a state of unusually high arousal, reactivity, or nervous system activation.",
    "aware of your shadow": "Conscious of one's disowned traits, projections, or rejected parts of the self (in a depth-psychology sense).",
    "shielded": "Emotionally protected or defended against perceived threat or hurt.",
    "integrated": "(Emotionally) bringing conflicting parts of the self into coherent wholeness.",
    "projecting": "Attributing one's own feelings or traits to others rather than owning them inwardly.",
    "rankled": "Sore or aggrieved on the inside from a lingering slight or resentment.",
    "tuned out": "Emotionally or attentionally disconnected from what is happening around oneself.",
    "unresponsive": "Not reacting outwardly to stimuli or others; flat or shut-down in expression.",
    "willing to change": "Open to revising oneself or one's behavior rather than defending the status quo.",
    "flagellating": "Figuratively or literally lashing at oneself with blame or harsh self-judgment.",
    "conscience-stricken": "Troubled by a strong sense of having done wrong.",
    "guilt-ridden": "Dominated by persistent guilt or self-reproach.",
    "guilt-stricken": "Suddenly or deeply struck by feelings of guilt.",
    "shamefaced": "Showing embarrassment or shame in one's manner or expression.",
    "speechless": "Unable to speak, often from shock, shame, or overwhelm.",
    "upstanding": "Honorable and respectable in character; principled.",
    "pleasureless": "Unable to feel enjoyment or satisfaction; flat to positive experience.",
    "passionless": "Lacking enthusiasm, desire, or emotional investment.",
    "awe-filled": "Filled with awe; deeply moved by wonder, grandeur, or the sacred.",
    "inward-focused": "Attending primarily to inner experience, meaning, or reflection rather than outward events.",
    "death-seeking": "Drawn toward death or ending one's life; an urgent signal to seek immediate help and support.",
    "gutted": "Emotionally devastated or hollowed out, as if emptied from within.",
    "feeling worthless": "Experiencing oneself as without value, dignity, or significance.",
    "scattered": "(Of attention or mind) fragmented and unable to settle; pulled in many directions at once.",
    "disconcerted": "Unsettled or thrown off balance; momentarily unsure how to feel or respond.",
    "curious": "Eager to know or understand; open interest toward what is happening (here often with light unease).",
    "comfortable": "Physically or emotionally at ease; free from strain, pain, or restless desire.",
    "devoted": "Lovingly loyal and committed; deeply attached and dependable.",
    "disrespected": "Feeling dismissed or treated as lacking worth, consideration, or dignity.",
    "threatened": "Feeling that safety, standing, or an important bond may be harmed or taken away.",
    "exhilarated": "Joyfully excited and energized; lifted by a rush of positive arousal.",
    "expansive": "Emotionally open or enlarged—generous in mood, or stretched toward big possibilities.",
    "playful": "Lighthearted and inclined toward fun, humor, or good-natured spontaneity.",
    "pleased": "Content or satisfied; quietly glad about how things are.",
    "thrilled": "Strongly excited and delighted; stirred by something positive.",
    "power-hungry": "Intensely driven to gain control, dominance, or influence over people or outcomes.",
    "resentful": "Bitter or indignant about a perceived unfairness, injury, or slight.",
    "restored": "Brought back toward strength, calm, or emotional wholeness after depletion or grief.",
}


def _placeholder(desc: str) -> bool:
    d = (desc or "").strip()
    return d.startswith("Emotional vocabulary term from the DEI list") or d.startswith(
        "Often used to avoid or hide deeper emotions"
    )


def _score_text(definition: str, pos_name: str) -> float:
    s = 0.0
    if _EMOTION_BOOST.search(definition):
        s += 4.0
    if pos_name in ("adjective", "satellite adjective"):
        s += 1.2
    if pos_name == "noun" and _EMOTION_BOOST.search(definition):
        s += 0.8
    if pos_name == "verb" and _EMOTION_BOOST.search(definition):
        s += 0.5
    if _IRRELEVANT.search(definition):
        s -= 5.0
    if 40 < len(definition) < 220:
        s += 0.2
    return s


def _wn_pos_name(syn) -> str:
    p = syn.pos()
    return {"s": "satellite adjective", "a": "adjective"}.get(p, p)


def _wordnet_best(term: str) -> str | None:
    variants = set()
    raw = term.strip()
    variants.add(raw)
    variants.add(raw.lower())
    variants.add(raw.replace("-", "_").replace(" ", "_").lower())
    variants.add(raw.replace("-", " ").lower())

    candidates: list[tuple[float, str]] = []
    for v in variants:
        if not v:
            continue
        lemma = v.replace(" ", "_")
        for syn in wn.synsets(lemma):
            pos = _wn_pos_name(syn)
            text = syn.definition().strip()
            if not text:
                continue
            sc = _score_text(text, pos)
            candidates.append((sc, text))
        for pos in (wn.ADJ, wn.ADJ_SAT):
            for syn in wn.synsets(lemma, pos=pos):
                text = syn.definition().strip()
                if text:
                    candidates.append((_score_text(text, "adjective"), text))

    if not candidates:
        return None
    candidates.sort(key=lambda x: (-x[0], len(x[1])))
    best_score, best_text = candidates[0]
    if best_score < 1.0:
        return None
    if not best_text.endswith((".", "!", "?")):
        best_text += "."
    return best_text[0].upper() + best_text[1:]


def _fetch_api(word: str) -> list | None:
    url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + urllib.parse.quote(
        word, safe=""
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 429:
                time.sleep(2.0 + attempt * 3)
                continue
            raise
        except urllib.error.URLError:
            time.sleep(1.0)
    return None


def _pick_api_definition(entry: dict) -> str | None:
    best: tuple[float, str] | None = None
    for meaning in entry.get("meanings", []):
        pos = meaning.get("partOfSpeech") or ""
        pmap = (
            "adjective"
            if pos == "adjective"
            else ("verb" if pos == "verb" else "noun")
        )
        for d in meaning.get("definitions", []):
            text = (d.get("definition") or "").strip()
            if not text:
                continue
            sc = _score_text(text, pmap)
            if best is None or sc > best[0]:
                best = (sc, text)
    if best and best[0] >= 1.0:
        t = best[1]
        if not t.endswith((".", "!", "?")):
            t += "."
        return t
    return None


def _api_definition(term: str) -> str | None:
    seen: set[str] = set()
    for attempt in (
        term.strip(),
        term.strip().replace("–", "-"),
        re.sub(r"\s+", " ", term.strip()),
        term.strip().replace("-", " "),
    ):
        if not attempt or attempt in seen:
            continue
        seen.add(attempt)
        raw = _fetch_api(attempt)
        time.sleep(API_DELAY)
        if not raw:
            continue
        picked = _pick_api_definition(raw[0])
        if picked:
            return picked
    return None


def _override(term: str) -> str | None:
    k = term.strip().casefold()
    for ok, ov in _OVERRIDES.items():
        if ok.casefold() == k:
            t = ov if ov.endswith((".", "!", "?")) else ov + "."
            return t
    return None


def definition_for_term(term: str) -> str | None:
    o = _override(term)
    if o:
        return o
    w = _wordnet_best(term)
    if w:
        return w
    return _api_definition(term)


def main() -> None:
    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    missing: list[str] = []
    filled = 0
    for obj in data:
        if not isinstance(obj, dict) or "term" not in obj:
            continue
        if not _placeholder(obj.get("description", "")):
            continue
        term = obj["term"]
        d = definition_for_term(term)
        if d:
            obj["description"] = d
            filled += 1
            if filled % 50 == 0:
                print("…", filled)
        else:
            missing.append(term)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("filled:", filled)
    print("still missing:", len(missing))
    for t in missing:
        print(" ", t)


if __name__ == "__main__":
    main()
