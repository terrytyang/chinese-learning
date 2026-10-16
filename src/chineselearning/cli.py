"""Command line: `chineselearning build` and `chineselearning serve`."""

import argparse
import os
import sys
from pathlib import Path

from . import db
from .texts import TextFileError

DATA_DIR = "data"
DEFAULT_DB = "build/content.sqlite"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="chineselearning")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="delete and rebuild the content database from data/")
    build.add_argument("--db", default=DEFAULT_DB, help="database path (default: build/content.sqlite)")
    commands.add_parser("serve", help="dev server on 0.0.0.0:8000 (database from $CHINESELEARNING_DB)")
    args = parser.parse_args(argv)
    if args.command == "build":
        try:
            counts = db.build(args.db, DATA_DIR)
        except TextFileError as e:
            sys.exit(f"build failed: {e}")
        print(f"{args.db}: " + ", ".join(f"{table} {n}" for table, n in counts.items()))
    elif args.command == "serve":
        path = Path(os.environ.get("CHINESELEARNING_DB", DEFAULT_DB))
        if not path.is_file():
            sys.exit(f"{path} does not exist; run `chineselearning build` first")
        import uvicorn

        uvicorn.run("chineselearning.web:app", host="0.0.0.0", port=8000)
