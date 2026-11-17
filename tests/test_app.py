import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app


def test_pages():
    client = app.test_client()
    for page in ["/", "/expert", "/climate", "/diseases"]:
        assert client.get(page).status_code == 200


def test_locales():
    client = app.test_client()
    for lang in ["pt", "en", "es"]:
        assert client.get("/expert?lang=" + lang).status_code == 200


def test_diagnosis():
    c = app.test_client()
    r = c.post(
        "/api/diagnose",
        json={
            "answers": {"manchas_amarelas": "sim", "folhas_murchas": "sim", "chuva_continua": "sim"}
        },
    )
    assert r.status_code == 200
    assert r.json["results"][0]["id"] == "mildio"
    assert r.json["results"][0]["confidence_percent"] == 70.0  # R02: CNF 70


def test_unknown_does_not_generate_diagnosis():
    client = app.test_client()
    assert client.post("/api/diagnose", json={"answers": {}}).json["results"] == []


def test_invalid_input():
    client = app.test_client()
    assert (
        client.post("/api/diagnose", json={"answers": {"poeira_branca": "nope"}}).status_code == 400
    )


def test_navigation_and_privacy_pages():
    client = app.test_client()
    for lang in ("pt", "en", "es"):
        for path in ("/", "/expert", "/climate", "/diseases", "/privacy"):
            response = client.get(f"{path}?lang={lang}")
            assert response.status_code == 200
            assert b"/static/app.js" in response.data
        privacy = client.get(f"/privacy?lang={lang}").get_data(as_text=True)
        assert "privacy" not in privacy.lower() or "<main" in privacy


def test_404_page_has_site_design_and_api_stays_plain():
    c = app.test_client()
    for lang, text in (
        ("pt", "Página não encontrada"),
        ("en", "Page not found"),
        ("es", "Página no encontrada"),
    ):
        r = c.get(f"/nao-existe?lang={lang}")
        assert r.status_code == 404
        html = r.get_data(as_text=True)
        assert (
            text in re.sub(r"<[^>]+>", "", html) and 'class="header' in html and "<footer" in html
        )
    assert c.get("/api/nao-existe").get_data(as_text=True) == "Not found"
