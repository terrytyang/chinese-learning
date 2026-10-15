# Text library, filters, and plain reader

The read-only FastAPI/Jinja2 library contains five classical works alongside the
existing HSK-1 data. Curated inputs and SQL exports preserve explicit IDs;
databases are disposable build outputs.

## Rebuild and restart

**Rebuild older text databases and restart the server.** The former
`library_text.category_id` schema and curated format version 1 are unsupported.
There is no migration or compatibility adapter. Choose fresh output paths:

```sh
uv run --locked chineselearning-init --extracted data/hsk-newest-level1.json --texts data/text-library.json --output build/library-filters-rebuilt.sqlite --sql-output build/library-filters-rebuilt.sql
cmp build/library-filters-rebuilt.sql data/hsk-text-library.sqlite.sql
CHINESELEARNING_DATABASE=build/library-filters-rebuilt.sqlite uv run --locked uvicorn chineselearning.web:create_app --factory --host 0.0.0.0 --port 8000
```

These commands run from the repository root in the development container. Use
`--host 127.0.0.1` on a host. Open port 8000 through VS Code port forwarding.
For subsequent builds, choose different output names. Existing runtime databases
are never modified in place. `build/library-filters-trial.sqlite` and
`build/library-filters-trial.sql` are the disposable outputs generated for this
increment; earlier trial databases are retained separately.

Only the two JSON inputs are needed for a combined build. The SQL snapshot can
restore the entire database without those files or the historical HSK source:

```sh
sqlite3 build/library-filters-restored.sqlite < data/hsk-text-library.sqlite.sql
sqlite3 build/library-filters-restored.sqlite 'PRAGMA integrity_check; PRAGMA foreign_key_check;'
```

Use a fresh destination. Python callers should decode the SQL file's UTF-8 bytes,
or open with `newline=""`, to preserve line endings inside SQL string literals.

## Version 2 input and schema

`data/text-library.json` has format `chineselearning-curated-texts`, version **2**.
The HSK extraction format is unchanged. A text record now contains category IDs
as a nonempty list:

```json
{
  "format": "chineselearning-curated-texts",
  "version": 2,
  "categories": [{"id": 1, "label": "诗词"}],
  "texts": [{
    "id": 1,
    "category_ids": [1],
    "author": "张继",
    "period": "唐朝",
    "title": "枫桥夜泊",
    "body": "月落乌啼霜满天，江枫渔火对愁眠。\n姑苏城外寒山寺，夜半钟声到客船。",
    "notes": null
  }]
}
```

The five category definitions retain their IDs: 1 诗词, 2 文言, 3 散文, 4 节选,
and 5 讲解. These are literary categories; no unrestricted thematic tagging
system is added. Additional category definitions require data changes only.

| Table | Fields and constraints |
| --- | --- |
| `text_category` | Explicit `id` primary key; required nonblank `label` |
| `library_text` | Explicit `id`; optional `author`, `period`, `notes`; required nonblank `title`, `body` |
| `text_category_assignment` | `text_id` and `category_id` foreign keys; composite primary key prevents duplicate assignments |

Category/text IDs must be positive 64-bit integers. The importer rejects duplicate
IDs, empty or duplicate category assignments, missing references, wrong field
types, unknown fields, unsupported versions, and blank required values. Required
text validation checks Unicode whitespace without trimming or rewriting content.
Optional fields may be omitted or null; omitted values become null. Explicit
empty strings remain empty. Notes remain null in all five saved works.

Text and category rows export by ID; assignments export by `(text_id, category_id)`.
Reordering arrays does not change identities or the SQL snapshot. SQL enforces
keys/references and basic nonblank text checks. The importer additionally enforces
Unicode nonblank values and at least one category per text; SQL alone does not
enforce the latter. Body punctuation and line/paragraph breaks remain exact.

`--texts FILE` works with both existing initialization modes. Omitting it leaves
all three text tables empty. The shared builder retains transactions, integrity
checks, protected inputs, overwrite refusal, and failure cleanup. No extraction,
import, or schema creation occurs during startup or HTTP requests. Startup still
validates the database; when text tables are present it requires the current
assignment schema. Databases predating text storage can still serve inventory
pages and an empty library.

## Library filters and reader

`GET /texts` accepts ordinary GET parameters `category_id`, `author`, and `period`.
The 类别、作者、年代 dropdowns each have 全部; 筛选 submits and 重置 clears filters.
Selections remain visible, with a result count and a no-results message.

- Category filtering matches any assignment; each text appears once.
- Author and period are exact, case-sensitive matches; active filters combine
  with AND. Empty values mean no filter. Values are bound SQL parameters.
- Category IDs must be positive 64-bit decimal integers; malformed values return
  HTTP 422 with a clear message. Valid values with no matches return HTTP 200.
- Texts are ordered by text ID. Assigned categories are displayed by category ID.
- Choices always come from the full library: assigned categories by ID, distinct
  nonblank authors/periods by Unicode order. Blank metadata and unused category
  definitions do not appear as choices. An unmatched submitted value is shown as
  a selected “无匹配值” option so it can be inspected/reset; it is not stored.

There is no pagination or JavaScript for this feature. The reader escapes all
imported content, preserves whitespace, omits missing author/period metadata,
and links back to the library. Notes are stored but never selected/displayed.
Unknown text IDs return HTTP 404. No editing, matching, annotation, pinyin,
exercise, account, or localization features are added.

## Sample works and reference choices

Full original wording was checked before import. Only the classical works are
included; modern notes, translations, pronunciation inserts, and the appended
《桃花源诗》 are excluded. Simplified characters and modern punctuation are used.
Poems have one couplet per line; 《桃花源记》 has five paragraphs separated by blank
lines. Period values use the requested dynasty labels, not precise composition
dates. Reference links and material choices:

| ID | Title / author / period / category | Reference and choice |
| --- | --- | --- |
| 1 | 枫桥夜泊 / 张继 / 唐朝 / 诗词 | Existing owner-supplied body and ID unchanged |
| 2 | 春晓 / 孟浩然 / 唐朝 / 诗词 | [Wikisource, with anthology references](https://zh.wikisource.org/zh-hans/春曉_(孟浩然)): use the main reading “夜来风雨声” and “花落知多少”; the page records “欲知昨夜风” and “无” variants |
| 3 | 赠汪伦 / 李白 / 唐朝 / 诗词 | [Wikisource, 全唐诗卷171](https://zh.wikisource.org/zh-hans/贈汪倫), cross-checked with [古文岛](https://m.gushiwen.cn/shiwenv_ca9eaf40a6ce.aspx): retain “将欲行”; the latter records “欲远行” as a manuscript variant |
| 4 | 绝句（迟日江山丽） / 杜甫 / 唐朝 / 诗词 | [Wikisource](https://zh.wikisource.org/zh-hans/絕句（遲日江山麗）), cross-checked with [古文岛](https://m.gushiwen.cn/gushiwen_d94549507d.aspx); preserve the disambiguating title; import only this complete four-line work |
| 5 | 桃花源记 / 陶渊明 / 东晋 / 文言 | [古文岛 original text](https://www.gushiwen.cn/GuShiWen.aspx?id=505e1de493), cross-checked against the [国文学习网 original](https://cerclearning.tp.edu.tw/classical/datapage/144) and [Wikisource](https://zh.wikisource.org/zh-hans/桃花源記) |

For 《桃花源记》, the selected simplified text follows 古文岛's prose wording and
five-paragraph structure, omitting its parenthetical pronunciation aids. It uses
“作食”; 国文学习网 has “做食”. It omits “为” before “设酒”; Wikisource retains that
word and appends the separate poem. The saved text ends at “后遂无问津者。”
Traditional forms such as 纔、彷彿、誌、餘、衣著 correspond to the saved simplified
才、仿佛、志、余、衣着. Modern punctuation follows the selected prose reference.
No extra categories are assigned just to demonstrate multiple assignments;
separate test fixtures cover that behavior.

## URLs, liveness, and dataset choice

With the server above:

- Library: `http://localhost:8000/texts`
- Readers: `/texts/1` 枫桥夜泊; `/texts/2` 春晓; `/texts/3` 赠汪伦;
  `/texts/4` 绝句（迟日江山丽）; `/texts/5` 桃花源记.
- Liveness: `http://localhost:8000/health`, HTTP 200 and `{"status":"ok"}`.

`/health` does no database/source work per request and exposes no internal details.
It confirms application liveness, not ongoing database readiness. Startup database
validation still occurs before the application can serve it.

The default database remains `build/inventory.sqlite`. Use the fixed 140-character
inventory database for `/`, whose sample-specific description is unchanged. Use
the combined database for `/texts`; `/api/characters` works with both datasets.

## Artifacts and verification

The combined snapshot is `data/hsk-text-library.sqlite.sql`: 248 characters, 294
vocabulary entries, five category definitions, five texts, and five assignments.
The existing HSK reading/meaning/constituent counts remain unchanged. All four SQL
snapshots are regenerated by the shared builder with clean DDL whitespace.
Historical files and previous character/HSK JSON inputs remain unchanged.

```sh
uv run --locked pytest -q
node tests/inventory_controller.test.mjs
git diff --check
```

Tests cover format/version validation, multiple assignments and restoration,
filters and dropdowns, escaping, exact body preservation, no-query liveness,
previous build modes, output protection/failure cleanup, and all saved snapshots.
No local browser or Playwright tooling was available; visible filter interaction,
navigation, Chinese fonts, and long-text layout remain visually unverified.
