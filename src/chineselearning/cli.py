"""Command line: `chineselearning build`, `serve` and `intake`."""

import argparse
import os
import sys
from pathlib import Path

from . import db
from .annotations import AnnotationError
from .texts import TextFileError

DATA_DIR = "data"
DEFAULT_DB = "build/content.sqlite"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="chineselearning")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="delete and rebuild the content database from data/")
    build.add_argument("--db", default=DEFAULT_DB, help="database path (default: build/content.sqlite)")
    commands.add_parser("serve", help="dev server on 0.0.0.0:8000 (database from $CHINESELEARNING_DB)")
    intake = commands.add_parser("intake", help="one-time: add auto words and non-master characters to a text's annotations")
    intake.add_argument("text_id", type=int)
    intake.add_argument("--force", action="store_true", help="redo the auto rows even if the text already has annotations")
    intake.add_argument("--db", default=DEFAULT_DB)
    intake.add_argument("--data", default=DATA_DIR)
    args = parser.parse_args(argv)
    if args.command == "build":
        try:
            counts = db.build(args.db, DATA_DIR)
        except (TextFileError, AnnotationError) as e:
            sys.exit(f"build failed: {e}")
        print(f"{args.db}: " + ", ".join(f"{table} {n}" for table, n in counts.items()))
    elif args.command == "serve":
        path = Path(os.environ.get("CHINESELEARNING_DB", DEFAULT_DB))
        if not path.is_file():
            sys.exit(f"{path} does not exist; run `chineselearning build` first")
        import uvicorn

        uvicorn.run("chineselearning.web:app", host="0.0.0.0", port=8000)
    elif args.command == "intake":
        from .intake import intake as run_intake

        try:
            counts = run_intake(db.connect(args.db), args.text_id, args.data, force=args.force)
        except AnnotationError as e:
            sys.exit(f"intake failed: {e}")
        print(f"text {args.text_id}: words {counts['words']}, characters {counts['characters']}")
