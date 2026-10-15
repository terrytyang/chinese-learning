# Project context

## Purpose

Build a Chinese learning and teaching system for a native Chinese-speaking
parent teaching a daughter currently in seventh grade. Chinese Level III credit
through Houston ISD CBE is a milestone; broader language, cultural, and literary
competence is the objective. Reverify assessment arrangements before making
consequential curriculum decisions.

## Working approach

- The owner is an experienced backend developer, strongest historically in
  Perl, familiar with Python and Java, and less experienced with frontend work.
- Work deliberately and collaboratively. Explain reasoning and tradeoffs;
  distinguish observed facts from inferences and proposals.
- Start in a VS Code Dev Container; anticipate hosted container development.
- Docker Compose also supports development and Codex outside VS Code using the
  same Dockerfile. It shares Codex state but uses a separate Python environment.
- Use `chineselearning` for the application distribution and Python package,
  and `chineselearning-init` for database initialization. The host checkout,
  container workspace paths, Docker resource names, and Codex state volume
  intentionally retain their existing names; see `.devcontainer/README.md`.
- Trial stack: Python 3.13, FastAPI, SQLAlchemy, Jinja2, and htmx. SQLite is the
  initial application database, separate from the historical source. Keep
  learning operations independent of presentation for future richer frontends.
- Do not create speculative application boilerplate or a large AGENTS.md.

## Existing HSK reference data

The original README.md, schema.sql, load_hsk.py, and hsk_vocab.sqlite are preserved
in `hsk-original/` as a historical reference dataset. Preserve their contents
and schema. The SQLite artifact is retained in Git alongside the source files.
Provenance is a low priority for this project. Run the original README's relative
commands from `hsk-original/`.

Read-only preflight found 11,470 vocabulary entries, 12,623 forms, 33,708 meanings,
1,746 classifiers, and 3,034 distinct characters. The schema file, embedded
loader schema, and live schema agree. Integrity and foreign-key checks passed.

The dataset contains separate `old`, `new`, and `newest` classifications. Its
character-level view derives the lowest level of a word containing a character;
it is not an independently imported official character syllabus. For example,
in the `new` scheme, 银行 is level 2 while the standalone 银 entry is level 3.
Character familiarity and word familiarity are separate dimensions.

## Agreed data direction

- Keep the HSK dataset largely as is. Build an independent model in new tables,
  initially referencing or drawing from it, and gradually remove the dependency
  as needed information is incorporated into the new model.
- New characters and vocabulary need independent identities and may have much
  richer properties than the source. HSK membership is optional.
- Vocabulary must include important expressions from taught texts even when
  absent from HSK. Absence does not itself imply high difficulty.
- Relationships may include compounds and expressions, usage and commonness,
  成语, 俗语, place names, loanwords, and context-specific meanings/readings.
- Preserve complete excerpts, poems, and classical texts as learning objects.
  Character, word, phrase, and literary annotations may overlap.
- Example interaction: display a passage with clickable characters at selected
  HSK levels and pronunciation on hover. Readings need contextual resolution.
- The source's radical field is not a complete character decomposition system.

## Rebuildable early development

The new model and curated import data should be maintained in importable source
files. A logical/meta schema and loaders or adapters may generate backend-specific
SQL. The early process is tear down and rebuild, not versioned data migration.

Aim for practical SQLite/PostgreSQL portability at the data-access boundary.
Do not build a general database framework or multi-platform migration system
prematurely. The owner expects the database choice to emerge before valuable,
non-rebuildable application state requires migrations. All these mechanisms
remain to be designed.

## Current next step

The first data milestone is a small rebuildable character database.
See `docs/database-bootstrap.md` for its commands, scope, and limitations.
English glosses start null and will be enriched separately after the schema
settles. Traditional forms are optional, retaining only one best-effort match.
Recognition and production have separate status references for a single trial
learner. HSK schemes and character levels live in related tables.

The eight-character seed and generated SQL snapshot are intended for source
control; application database files are disposable build outputs. The first
inventory page now adds FastAPI, Jinja2, plain CSS, and a fetch-based JavaScript
module. See `docs/character-inventory.md` for the saved 140-character selection,
read-only API, local server commands, and verification limitations. It retains
the normalized schema and the original eight-character fixture. Status editing,
pronunciation, content enrichment, learner accounts, and htmx remain deferred.
A separate [HSK extraction process](hsk-extraction.md) now saves versioned,
self-contained vocabulary/character JSON. Its first trial is `newest`, exact
level 1: 294 vocabulary entries, 248 characters, 396 reading/form records, and
1,115 meanings. Five vocabulary tables preserve independent application IDs,
optional ordered HSK memberships, source traditional forms/readings and ordered
meanings, and ordered character constituents. The initializer can build from
this JSON without the historical database. The eight- and 140-character seeds
remain separate fixtures; the inventory page still describes the latter.
The [text library and reader](text-library.md) now include 《枫桥夜泊》, 《春晓》,
《赠汪伦》, 《绝句（迟日江山丽）》, and 《桃花源记》. The first work retains its
original ID/body; the added works were checked against linked references, with
material textual choices documented. Curated format version 2 uses explicit
IDs and nonempty `category_ids` lists. `text_category_assignment` replaces the
former category column; category IDs 1–5 remain 诗词、文言、散文、节选、讲解.
No general thematic tagging framework is introduced. `--texts` imports these
records during fresh builds, and `data/hsk-text-library.sqlite.sql` restores
the combined HSK/text trial independently of the JSON files.

`/texts` supports exact category/author/period GET filters combined with AND,
with full-library dropdown choices and deterministic text/category ordering.
The reader preserves whitespace and escaping, omits missing metadata, and
keeps notes hidden. `/health` is constant application liveness without per-request
database work; it does not establish ongoing database readiness. Existing
startup validation is retained and requires the current assignment schema when
text tables are present. Rebuild older text databases and restart the server;
there is no old-format adapter or migration. The `/` page remains the
140-character sample and should use its inventory database; the character API
also works against the combined database. All four SQL snapshots were
regenerated through the shared builder, preserving clean DDL whitespace.

Character pronunciation, vocabulary learner state, text matching, annotations,
exercises, and automatic enrichment remain deferred. No migrations or stable-ID
infrastructure were added; curated inputs and exports preserve supplied IDs.

The project uses local Git on `main`; remote hosting remains undecided.
