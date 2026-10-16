from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from chineselearning import db
from chineselearning.web import create_app

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    """(db_path, counts) for a real build of data/ into a temporary file."""
    path = tmp_path_factory.mktemp("content") / "content.sqlite"
    return path, db.build(path, DATA_DIR)


@pytest.fixture(scope="session")
def client(built):
    return TestClient(create_app(built[0]))
