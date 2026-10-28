"""Pinyin helpers: numbered pinyin to tone marks, and pypinyin's readings for a supplement character."""

import re
import unicodedata

from pypinyin import Style, pinyin as _pinyin

TONE_MARKS = {"\u0304", "\u0301", "\u030c", "\u0300"}  # macron, acute, caron, grave: tones 1–4 as combining marks

MARKS = {"a": "āáǎà", "e": "ēéěè", "i": "īíǐì", "o": "ōóǒò", "u": "ūúǔù", "ü": "ǖǘǚǜ",
         "A": "ĀÁǍÀ", "E": "ĒÉĚÈ", "I": "ĪÍǏÌ", "O": "ŌÓǑÒ", "U": "ŪÚǓÙ", "Ü": "ǕǗǙǛ"}
NUMBERED = re.compile(r"([A-Za-züÜ:]+)([0-5])")


def _mark(match) -> str:
    letters, tone = match.group(1).replace("v", "ü").replace("V", "Ü").replace("u:", "ü").replace("U:", "Ü"), int(match.group(2))
    if tone in (0, 5):
        return letters
    lower = letters.lower()
    if "a" in lower:
        at = lower.index("a")
    elif "e" in lower:
        at = lower.index("e")
    elif "ou" in lower:
        at = lower.index("o")
    else:
        at = max(lower.rfind(v) for v in "iouü")
    if at < 0:
        return match.group(0)
    return letters[:at] + MARKS[letters[at]][tone - 1] + letters[at + 1:]


def to_marks(text):
    """`ti2` → `tí`, `lv4` → `lǜ`, `ni3 hao3` → `nǐ hǎo`; text without tone numbers is returned unchanged (None stays None)."""
    return NUMBERED.sub(_mark, text) if text else text


def toneless(text) -> str:
    """The syllables without tone marks (`shàng` → `shang`); ü keeps its diaeresis."""
    return "".join(c for c in unicodedata.normalize("NFD", text or "") if c not in TONE_MARKS)


def readings_of(char) -> list[str]:
    """pypinyin's readings of a character, most common first; empty when it has none."""
    return [r for r in _pinyin(char, style=Style.TONE, heteronym=True)[0] if r != char]
