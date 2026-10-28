"""Command line: `chineselearning build`, `serve` and `intake`."""

import argparse
import os
import sys
from pathlib import Path

from . import db
from .annotations import AnnotationError
from .supplement import SupplementError
from .texts import TextFileError

DATA_DIR = "data"
DEFAULT_DB = "build/content.sqlite"
DEFAULT_PROGRESS = "build/progress.sqlite"


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
    args = parser.parse_args(argv)
    if args.command == "build":
        try:
            counts = db.build(args.db, DATA_DIR)
        except (TextFileError, AnnotationError, SupplementError) as e:
            sys.exit(f"build failed: {e}")
        entries, unglossed = counts.pop("supplement"), counts.pop("supplement_unglossed")
        print(f"{args.db}: " + ", ".join(f"{table} {n}" for table, n in counts.items()))
        print(f"{entries} supplement entries, {unglossed} without a gloss")
    elif args.command == "serve":
        path = Path(os.environ.get("CHINESELEARNING_DB", DEFAULT_DB))
        if not path.is_file():
            sys.exit(f"{path} does not exist; run `chineselearning build` first")
        import uvicorn

        uvicorn.run("chineselearning.web:app", host="0.0.0.0", port=8000)
    elif args.command == "intake":
        from .intake import intake as run_intake, new_texts

        if args.new == (args.text_id is not None):
            intake.error("give one text id, or --new for every text with no facts and no lesson")
        conn = db.connect(args.db, progress_path=args.progress)
        ids = new_texts(conn) if args.new else [args.text_id]
        if not ids:
            print("nothing to intake: every text has facts or a lesson")
        for text_id in ids:
            try:
                counts = run_intake(conn, text_id, args.data, force=args.force)
            except AnnotationError as e:
                sys.exit(f"intake failed: {e}")
            print(f"text {text_id}: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
