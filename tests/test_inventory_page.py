from fastapi.testclient import TestClient

from chineselearning.web import create_app
from test_inventory_api import application_db


def test_page_shell_and_assets_share_the_api_application(application_db):
    with TestClient(create_app(application_db[0])) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        html = response.text
        for heading in ("Simplified character", "Traditional form", "English gloss", "HSK band",
                        "Recognition status", "Production status", "Usage note"):
            assert heading in html
        assert '<option value="7">7–9</option>' in html
        assert 'type="module"' in html
        assert 'scope="col"' in html and 'aria-sort="ascending"' in html
        assert 'role="status"' in html and 'for="band"' in html and 'for="page-size"' in html
        assert "placeholder trial state, not a student assessment" in html
        for asset in ("inventory.css", "inventory.js"):
            assert client.get(f"/static/{asset}").status_code == 200
        assert client.get("/api/characters").json()["total"] == 25
