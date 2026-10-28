"""Numbered pinyin to tone marks, and pypinyin's readings for a supplement character."""

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


def test_readings_of_lists_pypinyin_readings_most_common_first():
    assert pinyin.readings_of("啼") == ["tí"] and pinyin.readings_of("枫") == ["fēng"] and pinyin.readings_of("行")[:2] == ["xíng", "háng"]
    assert pinyin.readings_of("\U0002a6d6") == []
