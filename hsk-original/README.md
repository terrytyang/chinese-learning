# HSK vocabulary — raw SQLite import

A lossless SQLite copy of [drkameleon/complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary).

| | |
|---|---|
| Source commit | `7ac65bf1a6387d35f1ade478906172a19311c7f9` (2026-03-23) |
| Entries | 11,470 words · 12,623 forms (readings) · 33,708 meanings · 1,746 classifiers |
| Characters | 3,034 distinct |
| Level schemes | `old` = HSK 2.0 (1–6) · `new` = HSK 3.0, 2021 standard (1–7, where 7 = bands 7–9) · `newest` = HSK 3.0, 2026 syllabus (1–7) |

## Files

- `hsk_vocab.sqlite`: the database.
- `load_hsk.py`: the loader. Python 3.8+, standard library only.
- `schema.sql`: the schema, for reference (the loader embeds it; `python3 load_hsk.py --print-schema` prints it).

## Rebuilding or updating

```bash
git clone https://github.com/drkameleon/complete-hsk-vocabulary.git
python3 load_hsk.py complete-hsk-vocabulary hsk_vocab.sqlite --force
```

Every run:

1. Records the repo commit, commit date and SHA-256 of `complete.json` in `import_run`.
2. Stops with an error on any field it doesn't recognize, so an upstream format change can't be silently dropped.
3. Verifies itself. It rebuilds `complete.json` from the database and requires an exact match, then regenerates all 40 files under `wordlists/` from the `hsk_wordlist` view and requires exact matches. `import_run.verified = 1` only if both pass.

To update later, load the new commit into a **new file** and diff it against the old one before switching over. Nothing here is edited by hand; corrections and curriculum data belong in your own tables beside these.

## Tables

| Table | One row per | Notes |
|---|---|---|
| `import_run` | load | Provenance and verification flag. |
| `hsk_entry` | word | `entry_id` = position in `complete.json`, so original order is `ORDER BY entry_id`. `simplified` is unique. |
| `hsk_entry_level` | level tag | Raw tag plus parsed `scheme` and `level`. Order and duplicates kept: 7 entries (得 等 对 过 还 长 只) carry a repeated HSK 2.0 tag, apparently because the old list had them twice with different parts of speech. |
| `hsk_entry_pos` | part-of-speech code | Order kept. |
| `hsk_pos_code` | code | README meanings. `documented = 0` marks six codes seen in the data but not defined in the README: `Mg Rg cc mq qt qv`. |
| `hsk_form` | reading / traditional variant | Polyphones split here: 着 has four forms (zhāo, zháo, zhe, zhuó). All five transcriptions as columns. |
| `hsk_meaning` | meaning | Ordered within its form. |
| `hsk_classifier` | measure word | Ordered within its form. |
| `hsk_entry_char` | character position in a word | **Derived**, not in the source: `simplified` split into characters, so character queries are joins. |

## Views

| View | Purpose |
|---|---|
| `hsk_wordlist(kind, scheme, level, entry_id)` | Reproduces the repo's `wordlists/` files. "Exclusive" means *tagged with that level* and is not disjoint: a word tagged old-1 and old-2 is in both. "Inclusive" means tagged with any level up to N. |
| `hsk_entry_min_level(entry_id, scheme, level)` | Lowest level of each word, per scheme. |
| `hsk_char_min_level(char, scheme, level)` | Lowest level at which each character first appears in any word, per scheme. |
| `hsk_entry_flat` | One readable row per word (levels, POS, traditional, pinyin and meanings joined), for browsing. |

## Example queries

```sql
-- Character inventory for HSK 2.0 level 2: characters first appearing at that level
SELECT char FROM hsk_char_min_level WHERE scheme = 'old' AND level = 2;

-- Words made only of characters from a given set (here: HSK 2.0 levels 1–2)
WITH allowed AS (SELECT char FROM hsk_char_min_level WHERE scheme = 'old' AND level <= 2)
SELECT e.simplified FROM hsk_entry e
WHERE NOT EXISTS (SELECT 1 FROM hsk_entry_char c
                  WHERE c.entry_id = e.entry_id AND c.char NOT IN (SELECT char FROM allowed))
ORDER BY e.frequency;

-- Every word containing 客, with its level in two schemes
SELECT e.simplified, f.pinyin,
       (SELECT level FROM hsk_entry_min_level m WHERE m.entry_id = e.entry_id AND scheme = 'old') AS hsk20,
       (SELECT level FROM hsk_entry_min_level m WHERE m.entry_id = e.entry_id AND scheme = 'new') AS hsk30
FROM hsk_entry_char c
JOIN hsk_entry e USING (entry_id)
JOIN hsk_form f ON f.entry_id = e.entry_id AND f.form_seq = 1
WHERE c.char = '客'
ORDER BY e.frequency;

-- All readings and meanings of a polyphonic word
SELECT f.pinyin, m.meaning
FROM hsk_entry e JOIN hsk_form f USING (entry_id) JOIN hsk_meaning m USING (form_id)
WHERE e.simplified = '着'
ORDER BY f.form_seq, m.meaning_seq;

-- Distinct new characters per level, with running total
SELECT level, COUNT(*) AS new_chars, SUM(COUNT(*)) OVER (ORDER BY level) AS cumulative
FROM hsk_char_min_level WHERE scheme = 'new' GROUP BY level;
```

## Known characteristics of the source data

- **It is a word list, not a character dictionary.** Only 1,571 of the 3,034 characters have an entry of their own. Bound characters such as 客, 京, 脑 appear only inside words.
- **Its HSK 2.0 lists follow a different edition from hsk.academy**, which the HSK 1 materials were built on. Level 1 differs by six words (日 没 火车站 说话 零 饭馆 here, against 一点儿 号 哪儿 没有 说 饭店 there); 对, 等 and 过 sit at HSK 2.0 level 4 here but level 2 there.
- **Meanings come from CC-CEDICT**, at dictionary granularity, sometimes with cross-references as the first meaning (船: "variant of 船").
- **Ten erhua entries carry pinyin like `yǒukòngr5`.**
- **License:** the repo is MIT; the meanings derive from CC-CEDICT (CC BY-SA).

## Browsing

Any SQLite client opens the file: DB Browser for SQLite on the desktop, or [Datasette](https://datasette.io) for a local web UI with faceting and JSON output. For a custom website, the whole file (about 6 MB) can be queried directly in the browser with sql.js (SQLite compiled to WebAssembly), with no server.
