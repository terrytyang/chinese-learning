# Preliminary database initialization

This milestone builds a disposable application database containing eight
characters. The historical HSK database and its original files are unchanged.
There is no web server or migration system in this milestone.

## Run in the development container

```sh
uv sync --locked
uv run chineselearn-init --output build/trial.sqlite --sql-output build/trial.sql
uv run pytest
```

Run from the repository root. Both outputs must be new paths. For a subsequent
build, use different output names or explicitly remove only your disposable
outputs. There is deliberately no automatic overwrite or reset operation.
The builder prepares temporary files and publishes completed outputs without
overwriting existing files. A missing or invalid source selection produces no
published database or SQL snapshot.

To restore the committed snapshot without the historical source database:

```sh
sqlite3 build/restored.sqlite < data/bootstrap.sqlite.sql
sqlite3 build/restored.sqlite 'PRAGMA integrity_check; PRAGMA foreign_key_check;'
```

Use a fresh destination. Foreign-key enforcement is connection-specific in
SQLite. The import enables it for that connection; application connections must
also enable it. The supplied SQLAlchemy engine factory does so automatically.

## Files and authority

- `src/chineselearn/schema.py`: preliminary SQLAlchemy Core metadata; the logical
  schema definition. This uses existing schema machinery rather than a custom
  meta-schema language or an ORM object model.
- `data/bootstrap.json`: explicit ordered character selection and optional
  curated glosses/usage notes. These are currently all null.
- `hsk-original/hsk_vocab.sqlite`: read-only source of best-effort traditional forms and
  derived character classifications.
- `data/bootstrap.sqlite.sql`: generated, reviewable schema and seed snapshot.
  It is intended for version control and can initialize a fresh SQLite database
  independently. Do not edit it as a second independent source of truth.
- `build/`: ignored, disposable database and SQL outputs.
- `uv.lock`: locked dependencies for the Python 3.13 project environment.

When schema or seed inputs change, generate SQL to a fresh path, inspect its
diff against `data/bootstrap.sqlite.sql`, then replace that snapshot deliberately.
Future AI-assisted enrichment should edit the seed glosses/notes for review,
then regenerate the SQL. Construction performs no AI calls.

## Scope and deliberate limitations

The sample is 学, 银, 行, 客, 发, 后, 么, 服. It exercises shared characters,
polyphonic source entries, bound characters without standalone source entries,
and ambiguous traditional forms. Readings are not imported in this milestone.

The five tables are:

| Table | Purpose |
| --- | --- |
| `hanzi_character` | Independent ID, unique simplified character, optional traditional form, English gloss, and usage note |
| `hsk_scheme` | Source scheme code, label, and maximum level |
| `character_hsk_level` | One lowest level per character and scheme |
| `learning_status` | Integer-keyed codes: not_encountered, learning, known |
| `character_learning` | Separate recognition and production statuses for the single trial learner |

Character IDs are assigned from seed order, not copied from HSK entry IDs.
Reordering the seed may change IDs across fresh builds. Preserve the order while
comparing builds; stable identities across changing curricula are deferred.
Keys are explicit integers, not backend-generated sequences in this milestone.

Traditional selection first considers standalone entries, then shorter source
words. Ties use source entry ID, form order, and character position. Only forms
with equal simplified/traditional code-point lengths are eligible for positional
matching. Retain the first candidate, discard alternatives, and allow null when
none exists. This is intentionally lossy: 发 becomes 發 and 后 becomes 后 in
this snapshot. Neither is a promise of context-sensitive conversion.

Levels are the earliest vocabulary appearance of each character, not an
independent official character syllabus. All three source schemes are retained
separately. An absent classification is represented by no relation, not level 0.
The loader checks levels against each scheme's maximum; SQL constraints enforce
positive levels but do not independently enforce that cross-table maximum.

Glosses and usage notes are nullable and left blank until curated. Learning
statuses initially say not_encountered for both dimensions as placeholder trial
state, not an assertion about the student's actual knowledge. There are no
learner accounts, practice events, compound definitions, pronunciation tables,
or full character-variant relationships yet.

## Tests and portability

Tests build real SQLite files, compare selected records, verify bound-character
coverage and first traditional candidates, exercise constraints and independent
learning statuses, and import SQL into another fresh database. They also check
repeatability, source immutability, output protection, invalid selections,
Unicode/apostrophe/newline preservation, and snapshot freshness.

Generate schema SQL without creating files:

```sh
uv run chineselearn-init --print-schema sqlite
uv run chineselearn-init --print-schema postgresql
```

PostgreSQL DDL compilation is tested. PostgreSQL execution, full seed exports,
and behavioral compatibility are not yet verified. The generated snapshot is
explicitly SQLite SQL. Do not describe compilation as support for a tested
PostgreSQL application.
