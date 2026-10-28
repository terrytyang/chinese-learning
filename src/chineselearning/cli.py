"""Command line: `build`, `serve`, `intake`, `import-progress`, `export-progress` and `init`."""

import argparse
import os
import shutil
import sys
from pathlib import Path

from . import db, progress
from .annotations import AnnotationError
from .gloss_file import GlossFileError
from .progress_files import ProgressFileError
from .supplement import SupplementError
from .texts import TextFileError

DATA_DIR = "data"
BUILD_DIR = "build"
DEFAULT_DB = "build/content.sqlite"
DEFAULT_PROGRESS = "build/progress.sqlite"


def fail(step, error):
    sys.exit(f"{step} failed: {error}")


def build_command(db_path=DEFAULT_DB):
    try:
        counts = db.build(db_path, DATA_DIR)
    except (TextFileError, AnnotationError, GlossFileError, SupplementError) as e:
        fail("build", e)
    entries, unglossed = counts.pop("supplement"), counts.pop("supplement_unglossed")
    print(f"{db_path}: " + ", ".join(f"{table} {n}" for table, n in counts.items()))
    print(f"{entries} supplement entries, {unglossed} without a gloss")


def intake_command(db_path, data_dir, progress_path, text_id=None, new=False, force=False):
    from .intake import intake, new_texts

    conn = db.connect(db_path, progress_path=progress_path)
    ids = new_texts(conn) if new else [text_id]
    if not ids:
        print("nothing to intake: every text has facts or a lesson")
    for text_id in ids:
        try:
            counts = intake(conn, text_id, data_dir, force=force)
        except AnnotationError as e:
            fail("intake", e)
        print(f"text {text_id}: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    conn.close()


def import_command(files=(), check=False, learner_id=progress.LEARNER):
    from . import progress_import

    conn = db.connect(DEFAULT_DB, progress_path=DEFAULT_PROGRESS)
    try:
        print(progress_import.run(conn, DATA_DIR, files or None, check, learner_id).text())
    except (ProgressFileError, SupplementError) as e:
        fail("import-progress", e)
    conn.close()


def export_command(learner_id=progress.LEARNER):
    from . import progress_files

    conn = db.connect(DEFAULT_DB, progress_path=DEFAULT_PROGRESS)
    try:
        print(f"wrote {progress_files.export(conn, DATA_DIR, learner_id)}")
    except ProgressFileError as e:
        fail("export-progress", e)
    conn.close()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="chineselearning")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="delete and rebuild the content database from data/")
    build.add_argument("--db", default=DEFAULT_DB, help="database path (default: build/content.sqlite)")
    commands.add_parser("serve", help="dev server on 0.0.0.0:8000 (database from $CHINESELEARNING_DB)")
    intake = commands.add_parser("intake", help="one-time: auto words, readings and the default lesson for a text")
    intake.add_argument("text_id", type=int, nargs="?")
    intake.add_argument("--new", action="store_true", help="every text with no facts and no lesson, instead of one text id")
    intake.add_argument("--force", action="store_true", help="redo the auto rows even if the text already has annotations")
    intake.add_argument("--db", default=DEFAULT_DB)
    intake.add_argument("--data", default=DATA_DIR)
    intake.add_argument("--progress", default=DEFAULT_PROGRESS, help="learner database; recognized and mastered items stay out of the default lesson")
    imp = commands.add_parser("import-progress", help="resolve learner state from data/progress/ and data/import/progress/ (or FILE...) and write it")
    imp.add_argument("files", nargs="*", metavar="FILE")
    imp.add_argument("--check", action="store_true", help="print the report and write nothing")
    imp.add_argument("--learner", type=int, default=progress.LEARNER)
    exp = commands.add_parser("export-progress", help="write data/progress/<learner>.tsv from the learner database")
    exp.add_argument("--learner", type=int, default=progress.LEARNER)
    init = commands.add_parser("init", help="day-0: build, import-progress, intake --new")
    init.add_argument("--fresh", action="store_true", help="delete build/ first")
    args = parser.parse_args(argv)
    if args.command == "build":
        build_command(args.db)
    elif args.command == "serve":
        path = Path(os.environ.get("CHINESELEARNING_DB", DEFAULT_DB))
        if not path.is_file():
            sys.exit(f"{path} does not exist; run `chineselearning build` first")
        import uvicorn

        uvicorn.run("chineselearning.web:app", host="0.0.0.0", port=8000)
    elif args.command == "intake":
        if args.new == (args.text_id is not None):
            intake.error("give one text id, or --new for every text with no facts and no lesson")
        intake_command(args.db, args.data, args.progress, args.text_id, args.new, args.force)
    elif args.command == "import-progress":
        import_command(args.files, args.check, args.learner)
    elif args.command == "export-progress":
        export_command(args.learner)
    elif args.command == "init":
        if args.fresh:
            shutil.rmtree(BUILD_DIR, ignore_errors=True)
        build_command()
        import_command()
        intake_command(DEFAULT_DB, DATA_DIR, DEFAULT_PROGRESS, new=True)
