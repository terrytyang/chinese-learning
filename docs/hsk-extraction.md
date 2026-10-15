# HSK extraction and vocabulary loading

Extraction is an explicit development command. Neither application startup nor
HTTP requests read the historical HSK database or extract data. Database builds
from the extracted JSON also do not open the historical database. There are no
migrations: regenerate disposable databases from source files when needed.

## First trial and reproducible commands

Run from the repository root in the development container:

```sh
uv sync --locked
uv run --locked chineselearning-extract --source hsk-original/hsk_vocab.sqlite --settings data/hsk-newest-level1.selection.json --output build/hsk-newest-level1.json
cmp build/hsk-newest-level1.json data/hsk-newest-level1.json
uv run --locked chineselearning-init --extracted build/hsk-newest-level1.json --output build/hsk-newest-level1-rebuilt.sqlite --sql-output build/hsk-newest-level1-rebuilt.sql
cmp build/hsk-newest-level1-rebuilt.sql data/hsk-newest-level1.sqlite.sql
```

Every output must be a fresh path. For another run, choose other output names.
Extraction refuses an existing destination, including symlinks. The initializer
refuses existing database and SQL paths and paths aliasing its inputs. Both
commands protect their inputs; neither has an overwrite flag. The extractor
opens SQLite with `mode=ro`, `query_only`, and a read transaction. JSON is staged
and published exclusively. Database construction uses the shared transactional
builder with integrity/foreign-key checks and temporary outputs; handled failures
remove staged files and any outputs already published by that invocation.

The committed trial artifacts are:

| Path | Purpose |
| --- | --- |
| `data/hsk-newest-level1.selection.json` | Scheme `newest`, exact level `[1]` |
| `data/hsk-newest-level1.json` | Deterministic, self-contained extraction |
| `data/hsk-newest-level1.sqlite.sql` | Importable SQLite schema and data |
| `build/hsk-newest-level1.sqlite` | Disposable database from the first trial; ignored |

The original artifact generation commands were:

```sh
uv run --locked chineselearning-extract --source hsk-original/hsk_vocab.sqlite --settings data/hsk-newest-level1.selection.json --output data/hsk-newest-level1.json
uv run --locked chineselearning-init --extracted data/hsk-newest-level1.json --output build/hsk-newest-level1.sqlite --sql-output data/hsk-newest-level1.sqlite.sql
```

Those outputs now exist, so use the fresh `build/` paths above for verification.
To build directly from the committed JSON, without the historical source:

```sh
uv run --locked chineselearning-init --extracted data/hsk-newest-level1.json --output build/hsk-json-only.sqlite --sql-output build/hsk-json-only.sql
```

To restore from SQL alone, use a fresh destination:

```sh
sqlite3 build/hsk-restored.sqlite < data/hsk-newest-level1.sqlite.sql
sqlite3 build/hsk-restored.sqlite 'PRAGMA integrity_check; PRAGMA foreign_key_check;'
```

## Selection semantics

Pass either `--settings FILE` or all three selection flags. Settings contain
exactly `scheme`, `levels` (a nonempty list of distinct positive integers), and
`mode`. The source path remains an explicit CLI option and is not embedded as
an environment-dependent absolute path in the JSON. Flags equivalent to the
saved first trial are:

```sh
uv run --locked chineselearning-extract --source hsk-original/hsk_vocab.sqlite --scheme newest --levels 1 --mode exact --output build/hsk-exact1.json
```

- `--mode exact --levels 1 3` selects each entry tagged with level 1 **or** 3
  in the chosen scheme. It does not include entries tagged only at level 2.
  Entries tagged at several selected levels appear once. This uses tags,
  rather than the entry's minimum/first-appearance level.
- `--mode cumulative --levels 3` selects tags at levels 1 through 3 inclusive.
  Multiple requested levels use the highest one: `--levels 1 3` has the same
  cumulative result as `--levels 3`.
- Scheme codes must exist in the source (`old`, `new`, `newest` in this source).
  Levels must not exceed that scheme's maximum. The source stores the combined
  7–9 band as integer 7 for `new` and `newest`; 8 and 9 are not valid levels.
  Unknown schemes, empty results, duplicates, and invalid levels fail clearly.

Selection determines which vocabulary enters the document. Every selected entry
is included, including single-character vocabulary. All its constituent Unicode
code points are included. Character HSK levels remain the minimum appearance
across the **whole source**, rather than being recalculated from this selection.
All available source schemes and memberships are retained for selected vocabulary
and characters, including memberships outside the selected scheme/level.

## JSON contract and application schema

The UTF-8 document has `format: "chineselearning-hsk-extraction"`, `version: 1`,
selection settings, scheme definitions, characters, and vocabulary. Unknown
versions and invalid references/fields are rejected before database construction.
Vocabulary follows source entry order; characters follow Unicode order; selected
levels are sorted. Readings/forms, meanings, HSK memberships, and constituents
retain source order, including duplicates. There are no timestamps or machine
paths. Repeating the extraction from the same source/settings yields identical
bytes. `source_entry_id` is reference metadata in JSON, not an application key.

The existing five character tables remain intact. Five additional tables are:

| Table | Purpose |
| --- | --- |
| `vocabulary_entry` | Independent application ID and simplified word, phrase, or name |
| `vocabulary_reading` | Independent ID, entry and 1-based position, traditional form, pinyin, numeric, Wade–Giles, Bopomofo, and Romatzyh source fields |
| `vocabulary_meaning` | Reading ID, 1-based position, and meaning text |
| `vocabulary_hsk_level` | Entry ID, 1-based position, scheme, and level; ordered source memberships, including repeated tags |
| `vocabulary_character` | Entry ID, 1-based position, and character ID; repeated characters occupy separate positions |

Application IDs are assigned sequentially from document order, independently of
source IDs. IDs can change across fresh builds if source ordering changes. An
entry need not have HSK membership, and there is no uniqueness restriction on
vocabulary text that would prevent future distinct senses or homographs. For
manually extended JSON, `source_entry_id` may be null, memberships may be empty,
and readings may be empty. Required constituent characters must still be present.
The extraction command itself selects only actual HSK entries.

A reading row represents a source form, including its traditional variant;
identical pinyin on different forms is retained. Meanings belong to that specific
reading and are never flattened across forms. All six textual reading/form
fields are copied unchanged. Constituent positions are validated against the
simplified text. Database constraints enforce keys, foreign keys, positive
positions/levels, and unique reading positions within an entry. The loader also
validates contiguous list positions and scheme maxima; cross-table maxima and
text/constituent equality are not enforced by SQL alone.

Character traditional forms reuse the existing best-effort positional rule.
English glosses remain NULL, and word meanings are never copied to characters.
No character pronunciation is inferred by splitting vocabulary pinyin. Existing
character trial statuses are initialized as before; vocabulary has no learner
state. Part-of-speech tags, classifiers, radical/frequency fields, and historical
import-run provenance are not imported in this increment. There is no enrichment,
text storage/matching, annotation, exercise, or new vocabulary UI.

## Verified first-trial counts

Independent queries using distinct tagged source entries and splitting their
simplified strings found **294 vocabulary entries and 248 distinct characters**.
A separate query through `hsk_entry_char` found the same 248 characters and 470
positions. There is no discrepancy with the expected counts. Of the vocabulary
entries, 137 are single-character entries.

| Application records | Count |
| --- | ---: |
| Vocabulary | 294 |
| Characters | 248 |
| Reading/form records | 396 |
| Ordered meanings | 1,115 |
| Ordered vocabulary–character relations | 470 |
| Ordered vocabulary HSK memberships | 799 |
| Character HSK levels | 744 |
| Character learning records | 248 |
| Schemes / status definitions | 3 / 3 |

The eight-character bootstrap and fixed 140-character inventory manifests remain
separate regression fixtures. Their regenerated SQL snapshots include the new
empty tables and retain their existing data. The inventory API can query all
248 characters in the HSK database; the existing page still describes the saved
140-character sample, so use that fixture for the page. This increment adds no
page that presents or labels the HSK collection.

## Validation

```sh
uv run --locked pytest -q
node tests/inventory_controller.test.mjs
```

Tests cover exact/cumulative tag semantics, invalid selections, deterministic
bytes, source immutability and read-only access, protected inputs/outputs,
repeated constituents and memberships, reading/meaning/traditional associations,
JSON-only builds, SQL restoration, failure cleanup, independent IDs, vocabulary
without HSK membership, and the character API against both datasets. Existing
character-only databases remain readable by the API. Schema DDL compilation for
PostgreSQL remains a compilation check, not tested PostgreSQL execution.
