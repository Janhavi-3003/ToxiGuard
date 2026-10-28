"""
Shared NLP utilities for ToxiGuard (used by BOTH training and prediction).

Handles English, Tamil, Telugu, Hindi and their Roman-script versions
(Tanglish, Tenglish, Hinglish), plus obfuscation like "st*pid", "f@ck", "idi0t".
"""
import re
import unicodedata
from collections import Counter

# ---------------------------------------------------------------- cleaning
URL_RE = re.compile(r"(https?://\S+|www\.\S+)")
MENTION_RE = re.compile(r"(?<!\S)@\w+")
REPEAT_RE = re.compile(r"([a-z])\1{2,}")           # stuuuupid -> stuupid
LEET = str.maketrans({"@": "a", "0": "o", "1": "i", "3": "e", "$": "s",
                      "5": "s", "4": "a", "7": "t", "*": "u", "!": "i", "+": "t"})
EMOJI_MAP = {"\U0001F595": " middlefinger ", "\U0001F92C": " cursing "}


def _deleet(token):
    """Turn 'f@ck' -> 'fack', 'idi0t' -> 'idiot' (only for plain-ASCII tokens)."""
    if re.search(r"[^\x00-\x7f]", token):
        return token
    token = token.rstrip("!?.,")
    if len(re.findall(r"[a-z]", token)) < 2:
        return token
    if re.fullmatch(r"\d+[a-z]{1,3}|[a-z]{1,3}\d+", token):   # 5pm, mp3
        return token
    return token.translate(LEET)


def clean_text(text):
    if not isinstance(text, str):
        text = ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u200c", "").replace("\u200d", "")     # Indic joiners
    for emo, word in EMOJI_MAP.items():
        text = text.replace(emo, word)
    text = text.lower()
    text = URL_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    text = " ".join(_deleet(t) for t in text.split())
    # keep letters, combining marks (Tamil/Telugu/Hindi vowel signs) and digits
    text = "".join(ch if unicodedata.category(ch)[0] in "LMN" else " " for ch in text)
    text = REPEAT_RE.sub(r"\1\1", text)
    text = re.sub(r"\b\d+\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text):
    return text.split()


def _squeeze(s):
    return re.sub(r"([a-z])\1+", r"\1", s)


# ---------------------------------------------------------------- language
def detect_script(text):
    counts = {"ta": 0, "te": 0, "hi": 0}
    for ch in text:
        o = ord(ch)
        if 0x0B80 <= o <= 0x0BFF:
            counts["ta"] += 1
        elif 0x0C00 <= o <= 0x0C7F:
            counts["te"] += 1
        elif 0x0900 <= o <= 0x097F:
            counts["hi"] += 1
    lang, n = max(counts.items(), key=lambda kv: kv[1])
    return lang if n > 0 else None


LANG_NAMES = {"en": "English", "ta": "Tamil", "te": "Telugu", "hi": "Hindi"}

# Common Roman-script words used only to guess Tanglish / Tenglish / Hinglish
ROMAN_HINTS = {
    "ta": {"nee", "poda", "romba", "nandri", "vanakkam", "enna", "irukku", "irukeenga",
           "da", "dei", "naaye", "vaaya", "moodu", "nanba", "seri", "naan", "unna", "sethu"},
    "te": {"nuvvu", "meeru", "chala", "namaskaram", "dhanyavadalu", "ela", "unnaru",
           "bagundi", "ninnu", "noru", "musuko", "pora", "ra", "repu", "naaku"},
    "hi": {"tum", "tu", "aap", "nahi", "shukriya", "dhanyavad", "bahut", "kaise",
           "hai", "hain", "abe", "chup", "mujhe", "tujhe", "acha", "accha", "nikal"},
}

# ---------------------------------------------------------------- lexicon
# High-precision insult / threat list (native script + Roman script).
LEXICON = {
    "en": [
        "stupid", "idiot", "moron", "dumbass", "loser", "scum", "bastard", "fuck",
        "fucking", "fucker", "shit", "shitty", "bitch", "asshole", "bullshit", "slut",
        "whore", "retard", "worthless", "pathetic", "shut up", "go die", "kill yourself",
        "hate you", "kill you", "nobody likes you", "piece of shit", "middlefinger", "cursing",
    ],
    "ta": [
        "முட்டாள்", "லூசு", "பைத்தியம்", "நாயே", "மடையன்", "மண்டு", "பொறுக்கி", "கேவலம்",
        "அயோக்கியன்", "கழுதை", "வாயை மூடு", "வாய மூடு", "செத்துப்போ", "செத்து போ",
        "கொன்றுவிடுவேன்", "கொல்லுவேன்", "தண்டம்", "எருமை", "உபயோகமற்ற",
        "loosu", "naaye", "thevdiya", "otha", "punda", "koothi", "sunni", "madayan", "madaya",
        "vaaya moodu", "vaya moodu", "sethu poda", "sethupoda", "kolla poren", "konnuduven",
    ],
    "te": [
        "వెధవ", "దద్దమ్మ", "మూర్ఖుడు", "సన్నాసి", "పనికిమాలిన", "ఎందుకూ పనికిరావు",
        "నోరు మూసుకో", "చంపేస్తా", "చంపుతా", "దరిద్రుడు", "దరిద్రపు", "గాడిద",
        "vedhava", "dhaddamma", "murkhudu", "sannasi", "panikimalina", "noru musuko",
        "champestha", "champutha", "lanjakodaka", "lanja", "pichi vedhava",
    ],
    "hi": [
        "बेवकूफ", "हरामी", "कमीना", "कमीने", "घटिया", "निकम्मा", "नालायक", "उल्लू का पट्ठा",
        "चुप कर", "मुँह बंद कर", "मुंह बंद कर", "जान से मार", "मर जा", "मर जाओ",
        "चुतिया", "भोसड़ी", "मादरचोद", "बहनचोद", "रंडी", "गंदू",
        "bewakoof", "harami", "kamina", "kamine", "ghatiya", "nikamma", "nalayak",
        "ullu ka pattha", "chup kar", "muh band kar", "mooh band kar", "jaan se maar",
        "mar ja", "chutiya", "bhosdike", "madarchod", "behenchod", "randi", "gandu",
    ],
}

NEGATIONS = {"not", "never", "no", "dont", "don", "isnt", "isn", "aint", "cant", "wont"}
_ASCII_TERM = re.compile(r"^[a-z ]+$")
_SUFFIX = r"(?:s|es|ed|ing|y|a|e|u|i|o|ah)?"


def lexicon_hits(text):
    """Return (list_of_matched_terms, Counter_of_language_votes)."""
    cleaned = clean_text(text)
    sq = _squeeze(cleaned)
    hits, votes = [], Counter()
    for lang, terms in LEXICON.items():
        for term in terms:
            if _ASCII_TERM.match(term):
                pat = r"(?<![a-z])" + re.escape(_squeeze(term)) + _SUFFIX + r"(?![a-z])"
                m = re.search(pat, sq)
                if not m:
                    continue
                if lang == "en" and " " not in term:
                    prev = sq[:m.start()].split()[-2:]
                    if any(p in NEGATIONS for p in prev):     # "you are not stupid"
                        continue
                hits.append(term)
                votes[lang] += 1
            elif term in cleaned:                               # Indic script: substring
                hits.append(term)
                votes[lang] += 1
    return hits, votes


def guess_language(text, votes=None):
    """Return language code: ta / te / hi / en."""
    script = detect_script(text)
    if script:
        return script
    if votes:
        non_en = {k: v for k, v in votes.items() if k != "en"}
        if non_en:
            return max(non_en, key=non_en.get)
    tokens = set(clean_text(text).split())
    scores = {lang: len(tokens & words) for lang, words in ROMAN_HINTS.items()}
    lang, n = max(scores.items(), key=lambda kv: kv[1])
    return lang if n >= 1 else "en"
