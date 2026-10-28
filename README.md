# chineselearning

A private Chinese learning and teaching system: a native-speaking parent curating
texts (poems, classical prose, excerpts) and building character, vocabulary and
reading work for one student. HSK is a reference scale, not the curriculum.

Everything runs inside a container; see [`.devcontainer/README.md`](.devcontainer/README.md).
The data model and the reasoning behind it are in [`docs/design.md`](docs/design.md).
Development is done with Claude Code from briefs in [`docs/briefs/`](docs/briefs/).

```sh
uv sync --locked
uv run chineselearning build      # data/ -> build/content.sqlite
uv run chineselearning serve      # http://localhost:8000
uv run pytest -q
```

`hsk-original/` is the untouched reference dataset
([drkameleon/complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary)
as SQLite, see its README). `tools/derive_hsk.py` turns it into the two flat
tables in `data/hsk.sql` that the app actually uses.
