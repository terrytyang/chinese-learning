"""The UI check over tests/ui_manifest.py (marked ui): skipped with a message when Playwright's Chromium is not installed."""

from pathlib import Path

import pytest

from chineselearning import ui_check
from ui_manifest import PAGES

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.ui
def test_ui_check():
    if not ui_check.chromium_available():
        pytest.skip(ui_check.CHROMIUM_MISSING)
    results = ui_check.run(ROOT / "data", ROOT / "build" / "ui", PAGES)
    report = ui_check.report(results)
    print(report)
    assert all(r["ok"] for r in results), report
