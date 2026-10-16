import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from chineselearning import db
from chineselearning.web import create_app

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def copy_data(target):
    """A private copy of data/ without the owner's annotation files, so tests never depend on curation state."""
    shutil.copytree(DATA_DIR, target)
    shutil.rmtree(target / "annotations", ignore_errors=True)
    return target


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    """(db_path, counts) for a real build of data/ (texts and master only) into a temporary file."""
    folder = tmp_path_factory.mktemp("content")
    path = folder / "content.sqlite"
    return path, db.build(path, copy_data(folder / "data"))


@pytest.fixture(scope="session")
def client(built):
    return TestClient(create_app(built[0], progress_path=built[0].parent / "progress.sqlite"))


@pytest.fixture
def site(tmp_path):
    """A private copy of data/ (without annotations) and a database built from it; the app writes into the copy."""
    data = copy_data(tmp_path / "data")
    db_path = tmp_path / "content.sqlite"
    db.build(db_path, data)
    progress = tmp_path / "progress.sqlite"
    client = TestClient(create_app(db_path, data, progress), follow_redirects=False)
    return SimpleNamespace(data=data, db=db_path, progress=progress, client=client, file=data / "annotations" / "1.json")
