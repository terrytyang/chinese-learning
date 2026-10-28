"""The UI check (design.md, 2026-10-28): a headless browser drives every admin page and interaction of one manifest against
a copy of data/ served in-process, and fails a page on a console warning or error, a response of 400 or more that no
expect_422 step claimed, a server log record at WARNING or above, or bad geometry: a document wider than the viewport, an
element outside its nearest scrolling ancestor, a control wider than its table cell, overlapping pinyin, a `.zh` table cell with stacked text (over one and a half lines). Screenshots
and report.txt go to the output directory. `tests/test_ui.py` and `chineselearning ui-check` both run it."""

import logging
import shutil
import socket
import tempfile
import threading
import time
from pathlib import Path

VIEWPORT = {"width": 1366, "height": 768}
SETTLE_MS = 400  # the longest htmx delay on a page (300 ms) plus a little
CHROMIUM_MISSING = "Playwright's Chromium is not installed: run `uv run playwright install chromium`"

GEOMETRY = """() => {
  const issues = [], de = document.documentElement, text = el => (el.id ? '#' + el.id : el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ').join('.') : '')) + ' “' + el.textContent.trim().slice(0, 20) + '”';
  if (de.scrollWidth > window.innerWidth) issues.push(`the document is ${de.scrollWidth}px wide for a ${window.innerWidth}px viewport`);
  const scroller = el => { for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) { const s = getComputedStyle(a); if (/auto|scroll|hidden/.test(s.overflowX + ' ' + s.overflowY)) return a; } return null; };
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    const s = getComputedStyle(el); if (s.visibility === 'hidden' || s.position === 'fixed') continue;
    const sc = scroller(el), b = sc ? sc.getBoundingClientRect() : {left: 0, right: de.clientWidth};
    if (r.right > b.right + 1 || r.left < b.left - 1) issues.push(`${text(el)} extends outside ${sc ? text(sc) : 'the document'} (${Math.round(r.left)}–${Math.round(r.right)} vs ${Math.round(b.left)}–${Math.round(b.right)})`);
  }
  for (const td of document.querySelectorAll('td')) {
    const c = td.getBoundingClientRect();
    for (const el of td.children) { const r = el.getBoundingClientRect(); if (r.width && r.right > c.right + 1) issues.push(`${text(el)} extends outside its cell (${Math.round(r.right)} vs ${Math.round(c.right)})`); }
  }
  const rts = [...document.querySelectorAll('rt')].map(e => [e, e.getBoundingClientRect()]).filter(([, r]) => r.width && r.height);
  for (let i = 0; i < rts.length && issues.length < 40; i++) for (let j = i + 1; j < rts.length; j++) {
    const a = rts[i][1], b = rts[j][1];
    if (a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5) issues.push(`pinyin “${rts[i][0].textContent}” and “${rts[j][0].textContent}” overlap`);
  }
  for (const td of document.querySelectorAll('td.zh')) {
    const range = document.createRange(); range.selectNodeContents(td);
    const h = range.getBoundingClientRect().height, s = getComputedStyle(td), lh = parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.45;
    if (h > 1.5 * lh) issues.push(`${text(td)} is ${Math.round(h)}px tall, ${Math.round(h / lh * 10) / 10} lines (stacked)`);
  }
  return issues.slice(0, 40);
}"""


def copy_data(source, target, curation=True) -> Path:
    """A private copy of data/; without `curation` the annotation, lesson and progress files are left out, so tests never
    depend on the owner's curation state."""
    shutil.copytree(source, target)
    if not curation:
        for folder in ("annotations", "lessons"):
            shutil.rmtree(Path(target, folder), ignore_errors=True)
        for folder in ("progress", "import/progress"):
            for file in Path(target, folder).glob("*.tsv"):
                file.unlink()
    return Path(target)


class LogCapture(logging.Handler):
    """Every record at WARNING or above from the server and the app."""

    def __init__(self):
        super().__init__(logging.WARNING)
        self.records = []

    def emit(self, record):
        self.records.append(f"{record.levelname} {record.name}: {record.getMessage()}")


def serve(app):
    """The app on a free port in a thread; returns (server, port). Set `server.should_exit` to stop it."""
    import uvicorn

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_config=None, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(100):
        if server.started:
            return server, port
        time.sleep(0.05)
    raise RuntimeError("the server did not start")


def chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            p.chromium.launch().close()
        return True
    except Exception:  # not installed, or its executable missing
        return False


def run(data_dir, out_dir, pages) -> list[dict]:
    """Serve a copy of `data_dir` with a fresh progress database, drive every page of the manifest, write screenshots and
    report.txt under `out_dir`. Returns [{page, ok, reasons}]."""
    from playwright.sync_api import sync_playwright

    from . import db
    from .web import create_app

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="ui-check-"))
    data = copy_data(data_dir, work / "data")
    db.build(work / "content.sqlite", data)
    capture = LogCapture()
    logging.getLogger().addHandler(capture)
    server, port = serve(create_app(work / "content.sqlite", data, work / "progress.sqlite"))
    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(viewport=VIEWPORT)
            for spec in pages:
                results.append(check_page(context, f"http://127.0.0.1:{port}", spec, out_dir, capture))
            browser.close()
    finally:
        server.should_exit = True
        logging.getLogger().removeHandler(capture)
        shutil.rmtree(work, ignore_errors=True)
    (out_dir / "report.txt").write_text(report(results), encoding="utf-8")
    return results


def check_page(context, origin, spec, out_dir, capture) -> dict:
    name, reasons, console, responses, claimed = spec["name"], [], [], [], []
    page = context.new_page()
    page.on("console", lambda m: console.append(f"console {m.type}: {m.text}") if m.type in ("warning", "error") else None)
    page.on("pageerror", lambda e: console.append(f"page error: {e}"))
    page.on("response", lambda r: responses.append(r) if r.status >= 400 else None)
    capture.records.clear()
    try:
        page.goto(origin + spec["url"])
        settle(page)
        for step in spec.get("steps", ()):
            kind, selector, *rest = step
            if kind == "click":
                page.click(selector)
            elif kind == "fill":
                page.fill(selector, rest[0])
            elif kind == "select":
                page.select_option(selector, rest[0])
            elif kind == "expect":
                try:
                    page.wait_for_function("([s, t]) => [...document.querySelectorAll(s)].some(e => e.textContent.includes(t))", arg=[selector, rest[0]], timeout=5000)
                except Exception:
                    reasons.append(f"expected “{rest[0]}” in {selector}; got “{(page.text_content(selector) or '').strip()[:80] if page.query_selector(selector) else 'no such element'}”")
            elif kind == "expect_422":
                with page.expect_response(lambda r: r.status == 422, timeout=5000) as got:
                    page.click(selector)
                claimed.append(got.value)
            else:
                raise ValueError(f"unknown step {kind!r} on page {name}")
            settle(page)
        reasons += page.evaluate(GEOMETRY)
    except Exception as e:  # a selector that never appeared, a navigation that failed
        reasons.append(f"{type(e).__name__}: " + " | ".join(line.strip() for line in str(e).splitlines()[:3])[:300])
    for _ in claimed:  # Chromium logs a claimed 422 as a failed resource too
        line = next((c for c in console if "status of 422" in c), None)
        if line:
            console.remove(line)
    reasons += console
    reasons += [f"response {r.status} {r.request.method} {r.url.replace(origin, '')}" for r in responses if not any(r is c for c in claimed)]
    reasons += [f"server log: {r}" for r in capture.records]
    page.screenshot(path=str(out_dir / f"{name}.png"), full_page=True)
    page.close()
    return {"page": name, "ok": not reasons, "reasons": reasons}


def settle(page):
    page.wait_for_timeout(SETTLE_MS)
    page.wait_for_load_state("networkidle")


def report(results) -> str:
    """One line per page, then its reasons; identical reasons collapse into one line with a count."""
    lines = []
    for r in results:
        counts = {}
        for why in r["reasons"]:
            counts[why] = counts.get(why, 0) + 1
        lines.append(f"{'PASS' if r['ok'] else 'FAIL'} {r['page']}" + "".join(f"\n  - {why}" + (f" ×{n}" if n > 1 else "") for why, n in counts.items()))
    failed = sum(not r["ok"] for r in results)
    return "\n".join(lines) + f"\n{len(results)} pages, {failed} failed\n"
