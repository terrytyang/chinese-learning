# Brief 10 — Rebuild the admin page to match the mockup, with htmx

Read `CLAUDE.md`, `docs/design.md`, and the mockup
`docs/mockups/admin-page.dc.html` (open it in the design canvas if you can;
otherwise read the markup and the `renderVals` logic — it is the spec for
every control, label and behaviour below). Brief 09 is done.

## 1. htmx

Vendor `htmx.min.js` into `src/chineselearning/static/` (htmx 2.x, exact
version in a comment at the top of `base.html`), loaded on every page. Pattern
for the whole app from here: a page is a **shell** rendered once; regions are
**fragments** with their own GET; every mutation POSTs and returns the fragment
it changed (`hx-target` the region, `hx-swap="outerHTML"`); a validation
failure returns the same fragment with the error rendered at the form, status
422 (configure htmx to swap 422 responses). No redirects, no page anchors.
Non-htmx requests to a fragment URL get the full shell with that fragment in
place, so URLs are bookmarkable; `hx-push-url` on tab and filter changes.

## 2. Page: `/texts/{text}?lesson=<id>`

Match the mockup section by section.

**Shell**: back link; title; author · period; lesson `<select>` (changing it
reloads the tab region and the text block for that lesson, pushes the URL);
New lesson / Rename as small inline forms; "Open student view" link.

**Tags**: chips with ×, an add input; each change POSTs, rewrites the `tags:`
header line, returns the tags fragment.

**Text block**: ruby over every character; a summary line (characters, not in
HSK, without a gloss); **Edit pinyin** swaps the block for the edit form:
polyphones get a `<select>` of master readings, non-master characters a text
input (numbered pinyin accepted), single-reading characters static; Save
POSTs only changed positions as `manual` readings and returns the display
block; Cancel returns it unchanged.

**Tabs**: Characters · Words in text (included/total) · Expansions · Related
words · Notes, each a fragment at `/texts/{text}/lessons/{lesson}/<tab>`,
counts in the tab labels, active tab in the URL.

**Characters**: the lesson's characters (char, pinyin, level, gloss — inline
gloss and level inputs for non-master characters —, four state buttons,
Remove from lesson); then "Not in this lesson": level range, state filter
(default unconfirmed-or-exposed), include-not-in-HSK checkbox, checkboxes,
Select all shown, Add N to lesson.

**Words in text**: Show filter (default not yet reviewed), level range, shown
count, Add all shown to lesson, Mark all shown as reviewed; rows with include
checkbox, word, pinyin, level, gloss, origin badge, four state buttons, Edit
(inline pinyin + gloss), Delete (removes the text fact). Below: add a word that
appears in the text — Look up; if not an HSK word, the second form (pinyin
prefilled, gloss, level default 7, state default exposed).

**Expansions**: one block per lesson character in lesson order: character and
pinyin; its extra words with one-character anchor = this character (word,
pinyin, level, gloss, origin, state buttons, Edit, Delete); input + "Look up &
add"; the two-step second form when not an HSK word.

**Related words**: table (anchor, word, pinyin, level, gloss, origin, state,
Edit, Delete) of extra words whose anchor is not a single character; add form
with optional anchor + word + Look up; two-step as above.

**Notes**: anchor, note, origin, Delete; add form.

Vocabulary everywhere: Add to lesson / Remove from lesson for selection;
Delete only when the thing itself is removed.

## 3. Code shape

`admin.py` becomes a package or a few modules (shell, text block, one per
tab), none over ~200 lines; one Jinja partial per fragment. The existing
annotation/lesson/progress modules are the data layer and should need little
change beyond brief 09.

## 4. Tests

Fragment tests with the `HX-Request` header asserting the returned fragment;
full-page tests asserting the shell contains the default tab; the pinyin edit
round trip; bulk add; Words-in-text filters and bulk actions; two-step
expansion (master word → linked; local → second form → created); 422 returns
the fragment with the error at the form; tag add/remove rewrites only the
`tags:` line.

## Acceptance

Walk the mockup against the real page with `/texts/1` and lesson "Learn
枫桥夜泊": every control present, every action updates its region without a
page reload or scroll jump. `uv run pytest -q` passes.

## Not in this brief

Student page changes beyond what brief 09 did, print, exercises, styling pass,
per-position reading overrides from anywhere but edit mode.
