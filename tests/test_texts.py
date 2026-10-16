import pytest

from chineselearning.texts import TextFileError, load_texts, parse_text

GOOD = "id: 1\ntitle: 枫桥夜泊\nauthor: 张继\nperiod: 唐朝\ntags: 诗词\n\n月落乌啼霜满天，\n江枫渔火对愁眠。\n"


def test_header_and_body():
    t = parse_text(GOOD)
    assert (t.id, t.title, t.author, t.period, t.tags) == (1, "枫桥夜泊", "张继", "唐朝", ["诗词"])
    assert t.notes is None
    assert t.body == "月落乌啼霜满天，\n江枫渔火对愁眠。"


def test_body_is_verbatim_except_final_newline():
    t = parse_text("id: 2\ntitle: x\ntags: a\n\n第一段\n\n第二段\n\n")
    assert t.body == "第一段\n\n第二段\n"


def test_optional_fields_and_multiple_tags():
    t = parse_text("id: 3\ntitle: x\ntags: 文言, 节选，讲解\nnotes: 备注\n\n正文")
    assert t.tags == ["文言", "节选", "讲解"]
    assert t.author is None and t.notes == "备注"


def test_value_may_contain_colon():
    assert parse_text("id: 4\ntitle: 绝句：其一\ntags: 诗词\n\n正文").title == "绝句：其一"


@pytest.mark.parametrize(
    "source, reason",
    [
        ("title: x\ntags: a\n\n正文", "missing header key 'id'"),
        ("id: 1\ntags: a\n\n正文", "missing header key 'title'"),
        ("id: 1\ntitle: x\n\n正文", "missing header key 'tags'"),
        ("id: 1\ntitle: x\ntags: ,\n\n正文", "at least one"),
        ("id: one\ntitle: x\ntags: a\n\n正文", "integer"),
        ("id: 1\ntitle: x\ntags: a\nfoo: bar\n\n正文", "unknown header key 'foo'"),
        ("id: 1\nid: 2\ntitle: x\ntags: a\n\n正文", "duplicate header key 'id'"),
        ("id: 1\ntitle: x\ntags: a\nno colon here\n\n正文", "bad header line"),
        ("id: 1\ntitle: x\ntags: a\n正文", "no blank line"),
        ("id: 1\ntitle: x\ntags: a\n\n", "empty body"),
        ("id: 1\ntitle: x\ntags: a\n\n\n   \n", "empty body"),
    ],
)
def test_rejects_bad_files(source, reason):
    with pytest.raises(TextFileError, match=reason):
        parse_text(source, name="bad.md")


def test_error_names_the_file():
    with pytest.raises(TextFileError, match=r"^bad\.md: "):
        parse_text("title: x\n\n正文", name="bad.md")


def test_load_texts_rejects_duplicate_id(tmp_path):
    (tmp_path / "a.md").write_text("id: 1\ntitle: a\ntags: t\n\n甲", encoding="utf-8")
    (tmp_path / "b.md").write_text("id: 1\ntitle: b\ntags: t\n\n乙", encoding="utf-8")
    with pytest.raises(TextFileError, match="duplicate id 1"):
        load_texts(tmp_path)
