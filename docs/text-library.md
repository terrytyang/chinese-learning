# Text library and plain reader

The text library is a small, read-only addition to the existing FastAPI/Jinja2
application. The first imported work is 《枫桥夜泊》, with the author, period, and
body supplied by the owner. No commentary or missing metadata is invented.

## Build and open the reader

Run from the repository root in the development container, using fresh outputs:

```sh
uv run --locked chineselearning-init --extracted data/hsk-newest-level1.json --texts data/text-library.json --output build/hsk-text-library-rebuilt.sqlite --sql-output build/hsk-text-library-rebuilt.sql
cmp build/hsk-text-library-rebuilt.sql data/hsk-text-library.sqlite.sql
CHINESELEARNING_DATABASE=build/hsk-text-library-rebuilt.sqlite uv run --locked uvicorn chineselearning.web:create_app --factory --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/texts` through VS Code port forwarding. The sample
reader is `http://localhost:8000/texts/1`. Use `--host 127.0.0.1` when running
directly on a host instead of inside the container.

`build/hsk-text-library.sqlite` and `build/hsk-text-library.sql` are the original
disposable trial outputs. The command above uses different names so those files
remain intact. Choose new names again for subsequent builds. Do not change a
runtime database in place; build another file and restart the server against it.

Only the two JSON files are needed for the combined build; the historical HSK
database is not opened. Startup and HTTP requests only read the existing
application database. No extraction, import, or schema creation runs in the web
application.

The generated `data/hsk-text-library.sqlite.sql` restores the entire combined
database without either JSON input or the historical dataset:

```sh
sqlite3 build/hsk-text-library-restored.sqlite < data/hsk-text-library.sqlite.sql
sqlite3 build/hsk-text-library-restored.sqlite 'PRAGMA integrity_check; PRAGMA foreign_key_check;'
```

Use a fresh restore destination. Python callers restoring SQL should read its
bytes and decode UTF-8, or open with `newline=""`, to avoid text-mode newline
translation inside SQL string literals.

## Saved inputs and schema

`data/text-library.json` uses a separate format from HSK extraction:

```json
{
  "format": "chineselearning-curated-texts",
  "version": 1,
  "categories": [{"id": 1, "label": "诗词"}],
  "texts": [{
    "id": 1,
    "category_id": 1,
    "author": "张继",
    "period": "唐朝",
    "title": "枫桥夜泊",
    "body": "月落乌啼霜满天，江枫渔火对愁眠。\n姑苏城外寒山寺，夜半钟声到客船。",
    "notes": null
  }]
}
```

The saved input defines all five initial categories: ID 1 诗词, 2 文言, 3 散文,
4 节选, and 5 讲解. Category and text IDs are supplied explicitly as positive
64-bit integers. They are copied unchanged into the application and SQL export;
array order does not assign identities. Records are inserted/exported in ID
order. Keep IDs and their references consistent when editing curated inputs.
There is no ID registry, automatic identity allocation, or migration machinery.

Two tables extend the existing schema:

| Table | Columns |
| --- | --- |
| `text_category` | `id` primary key, required nonblank `label` |
| `library_text` | `id` primary key, required `category_id` foreign key, optional `author`/`period`, required nonblank `title`/`body`, optional `notes` |

One text has one category. Additional categories require data changes only.
There is no required relationship to HSK characters or vocabulary, so a text may
contain characters absent from the HSK selection. There are no annotation or
matching tables in this increment.

The importer rejects duplicate IDs, missing category references, wrong field
types, unknown fields, unsupported formats/versions, and whitespace-only required
values. It checks Unicode whitespace without trimming or rewriting the stored
values. Body punctuation, spaces, and line endings are preserved exactly.
SQL constraints also enforce keys/references, required values, and empty or
space-only labels/titles/bodies; the importer handles the broader Unicode
whitespace check. Optional `author`, `period`, and `notes` may be omitted, null,
or text. Omitted fields become null; explicit empty strings remain empty.

`--texts FILE` is optional and works with both `--extracted FILE` and the existing
character-seed build mode. With no `--texts`, fresh databases contain empty text
tables. It uses the existing transaction, integrity checks, SQL generator, input
and overwrite protections, and failure cleanup. Text inputs are protected as
well as HSK/character inputs. Every output path must be fresh.

## Pages and dataset choice

| Page | Appropriate database |
| --- | --- |
| `/texts`, `/texts/1` | Combined HSK/text trial for the poem; no-text builds show an empty library |
| `/` | Fixed 140-character inventory built from `data/inventory.json`; its sample-specific description is unchanged |
| `/api/characters` | Character fixture, HSK-only, or combined database; counts reflect the chosen database |

The server defaults to `build/inventory.sqlite`. Set `CHINESELEARNING_DATABASE`
explicitly for the combined trial. Opening `/` with that database still shows
the existing sample-specific page shell; use `/texts` for this trial and the
140-character database when evaluating the inventory page.

The library lists titles linked to their readers, categories, authors, and
periods, ordered by explicit text ID ascending. An empty library says
“暂无文章。” Pre-library databases lacking text tables also show that empty state
and keep their existing inventory behavior.

The reader uses Chinese metadata labels, visually preserves whitespace and line
breaks, and links back to the library. Unknown IDs return HTTP 404. Missing
optional author/period fields are omitted. Jinja autoescaping applies to all
imported values; they are never trusted HTML. Editorial notes are stored but
not selected or automatically displayed by either page.

There is no editing UI, text lookup/highlighting, vocabulary segmentation,
annotation, teaching association, pinyin, hover definition, exercise,
authentication, student results, or localization framework.

## Artifacts and verification

The combined trial contains 248 characters, 294 vocabulary entries, 396
reading/forms, 1,115 meanings, 470 constituent relations, 799 vocabulary HSK
memberships, 744 character HSK relations, five categories, and one text. The
original eight- and 140-character manifests and the HSK extraction JSON remain
unchanged. Their SQL snapshots were regenerated with empty text tables and
clean DDL whitespace.

```sh
uv run --locked pytest -q
node tests/inventory_controller.test.mjs
git diff --check
```

Tests cover explicit ID/reference preservation, invalid imports, exact Unicode
and line endings, combined builds and SQL-only restoration, previous build
modes, output protection and failure cleanup, and library/reader responses,
escaping, empty states, and missing IDs. Snapshot tests cover all four saved SQL
exports. No browser or Playwright tooling was installed during implementation;
visual rendering, Chinese fonts, narrow-screen wrapping, and keyboard interaction
remain unverified. The HTTP tests check rendered HTML and the shipped CSS.
