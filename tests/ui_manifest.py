"""Every admin page and htmx interaction, for the UI check (chineselearning.ui_check). A page is a URL and ordered steps:
click(selector), fill(selector, text), select(selector, value), expect(selector, text), expect_422(selector) for a click whose
response is a deliberate 422. Pages run in order against one copy of data/ with a fresh progress database, so a page may
rely on what an earlier one made. A brief that touches a page adds its pages and interactions here."""

PAGES = [
    {"name": "texts", "url": "/texts", "steps": [
        ("expect", "h1", "Texts"),
        ("click", "#vocabulary button"),  # New lesson: the first vocabulary lesson, empty
        ("expect", "#vocabulary", "Vocabulary lessons · 1"),
    ]},
    {"name": "import", "url": "/texts/import", "steps": [
        ("fill", "textarea[name=body]", "床前明月光，疑是地上霜。"),
        ("expect", "#preview", "title"),
        ("expect_422", "#import button[hx-post='/texts/import']"),  # no title yet
        ("expect", "#import .error", "title"),
        ("fill", "input[name=title]", "静夜思二"),
        ("fill", "input[name=author]", "李白"),
        ("expect", "#preview", "id: "),
        ("click", "#import button[hx-post='/texts/import']"),
        ("expect", "#import .done", "Written"),
    ]},
    {"name": "text", "url": "/texts/1", "steps": [
        ("expect_422", "#lesson-controls form:nth-of-type(1) button"),  # New lesson with a blank name
        ("expect", "#lesson-controls .error", "required"),
        ("fill", "#lesson-controls form:nth-of-type(1) input[name=name]", "Level 1"),
        ("click", "#lesson-controls form:nth-of-type(1) button"),
        ("expect", "#lesson-controls select[name=lesson]", "Level 1"),  # the new, empty lesson is current
        ("click", "#tabs input[name=chars]"),  # Characters: tick a candidate and add it
        ("click", "#tabs button[data-count]"),
        ("click", "#tabs tr[id^=char-] form.states button[value=recognized]"),  # a state button on the study row
        ("expect", "#tabs tr[id^=char-] form.states button.on", "recognized"),
        ("click", "a.tab[href$='/expansions']"),
        ("fill", "#tabs .block input[name=surface]", "月亮"),  # the first block's add form
        ("click", "#tabs .block form.inline button"),
        ("expect", "#tabs", "月亮"),
        ("click", "a.tab[href$='/related']"),
        ("fill", "#tabs form.inline input[name=surface]", "半夜"),
        ("click", "#tabs form.inline button.primary"),
        ("expect", "#tabs tr[id^=extra-]", "半夜"),
        ("click", "a.tab[href$='/notes']"),
        ("fill", "#tabs input[name=note]", "首句写景"),
        ("click", "#tabs form.inline button.primary"),
        ("expect", "#tabs tr[id^=note-]", "首句写景"),
        ("fill", "#tags input[name=tag]", "七绝"),
        ("click", "#tags form button"),
        ("expect", "#tags", "七绝"),
        ("click", "#text button[hx-get$='/text/edit']"),  # Edit pinyin, then cancel
        ("expect", "#text", "Save readings"),
        ("click", "#text button[hx-get$='/text']"),
        ("expect", "#text", "Edit pinyin"),
    ]},
    {"name": "text-words", "url": "/texts/5/lessons/5/words", "steps": [  # the Words in text tab needs a text with words
        ("select", "#tabs select[name=show]", "all"),
        ("expect", "#tabs", "shown"),
        ("click", "#tabs tr[id^=word-] input[name=in]"),  # include the first word in the lesson
        ("click", "#tabs tr[id^=word-] button[hx-get]"),  # its inline edit
        ("fill", "#tabs form.inline input[name=gloss]", "contextual"),
        ("click", "#tabs form.inline button.primary"),
        ("expect", "#tabs tr[id^=word-]", "contextual"),
    ]},
    {"name": "dictionary", "url": "/dictionary", "steps": [
        ("fill", "#q", "乌"),
        ("expect", "#shown", "5 shown"),
        ("select", "#filters select[name=kind]", "word"),
        ("expect", "#shown", "3 shown"),
        ("click", "#entry-乌鸦 form.states button[value=exposed]"),
        ("expect", "#entry-乌鸦 form.states button.on", "exposed"),
        ("click", "#entry-乌鸦 button[hx-get$='edit=1']"),
        ("fill", "#entry-乌鸦 input[name=gloss]", "crow (bird)"),
        ("click", "#entry-乌鸦 form.inline button.primary"),
        ("expect", "#entry-乌鸦 td.gloss", "crow (bird)"),
        ("select", "#rows select[name=lesson]", "new"),
        ("click", "#rows form button"),  # Add all 3 shown to a new lesson
        ("expect", "#rows", "Added 3 to"),
        ("fill", "#add input[name=item]", "乌鸦"),
        ("click", "#add form.inline button"),
        ("expect", "#add", "Already in the dictionary"),
        ("fill", "#add input[name=item]", "月霜"),
        ("click", "#add form.inline button"),
        ("expect", "#add", "is not in the dictionary"),
        ("fill", "#add input[name=gloss]", "moon frost"),
        ("click", "#add form.local button"),
        ("expect", "#add", "Added to the supplement"),
        ("expect_422", "#add form.inline button"),  # Look up with a blank item
        ("select", "#filters select[name=changed]", "on"),
        ("expect", "#date option", "("),
        ("select", "#filters select[name=changed]", "after"),
    ]},
    {"name": "lesson-empty", "url": "/texts", "steps": [  # the empty lesson the texts page made, renamed for the duplicate below
        ("click", "#vocabulary li:nth-child(2) a"),
        ("expect", "h1, #header", "characters"),
        ("fill", "#header input[name=name]", "Empty"),
        ("click", "#header button"),
        ("expect", "#header", "0 characters"),
    ]},
    {"name": "lesson", "url": "/texts", "steps": [  # the lesson the dictionary page filled
        ("click", "#vocabulary li:nth-child(1) a"),
        ("expect", "#header", "3 words"),
        ("fill", "#header input[name=name]", "Empty"),
        ("expect_422", "#header button"),
        ("expect", "#header .error", "already exists"),
        ("fill", "#header input[name=name]", "Birds"),
        ("click", "#header button"),
        ("expect", "#header", "0 characters · 3 words"),
        ("click", "#members tr[id^=member-] button"),  # Remove the first member
        ("expect", "#members .sec", "Words · 2"),
        ("click", "#members form[hx-post$='/mark'] button"),  # Mark all as recognized
        ("expect", "#members", "raised to recognized"),
        ("fill", "#notes input[name=note]", "review on Friday"),
        ("click", "#notes form.inline button.primary"),
        ("expect", "#notes", "review on Friday"),
    ]},
    {"name": "learn", "url": "/learn", "steps": [("expect", "h1", "Learn")]},
    {"name": "reader", "url": "/learn/1/1?pinyin=1&words=1&gloss=1&tint=level", "steps": [("expect", "h1", "枫桥夜泊")]},
    {"name": "reader-long", "url": "/learn/5?pinyin=1&traditional=1", "steps": [("expect", "h1", "桃花源记")]},
]
