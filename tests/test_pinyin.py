"""Numbered pinyin to tone marks, and the pypinyin fallback for characters the master lacks."""

import pytest

from chineselearning import pinyin


@pytest.mark.parametrize(
    "numbered, marked",
    [
        ("ti2", "tí"), ("lv4", "lǜ"), ("nv3", "nǚ"), ("lu:4", "lǜ"), ("ni3 hao3", "nǐ hǎo"), ("xian1", "xiān"), ("liu2", "liú"),
        ("gui4", "guì"), ("ou3", "ǒu"), ("hui2", "huí"), ("ma5", "ma"), ("ma0", "ma"), ("Han2 Shan1 Si4", "Hán Shān Sì"),
        ("yue4liang5", "yuèliang"), ("tí", "tí"), ("yuè liang", "yuè liang"), ("", ""), (None, None), ("m2", "m2"),
    ],
)
def test_to_marks(numbered, marked):
    assert pinyin.to_marks(numbered) == marked


def test_guess_is_none_for_a_character_pypinyin_lacks():
    assert pinyin.guess("啼") == "tí" and pinyin.guess("枫") == "fēng"
    assert pinyin.guess("\U0002a6d6") is None
