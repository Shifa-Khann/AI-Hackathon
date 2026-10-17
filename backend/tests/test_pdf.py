import pytest
from conftest import AYESHA, onboard


def _edition(client):
    uid, h = onboard(client, AYESHA)
    ed = client.post("/api/editions/generate", headers=h).json()
    user = client.get("/api/profile", headers=h).json()["user"]
    return ed, user


def test_html_has_masthead_and_end_panel(client):
    from app import pdf

    ed, user = _edition(client)
    html = pdf.render_html(ed, user)
    assert "The Fold" in html and f"Edition No. {ed['number']}" in html
    assert "That&#39;s the paper." in html or "That's the paper." in html
    assert ed["items"][0]["headline"] in html
    assert "data:image/svg+xml;base64" in html, "QR codes expected"
    assert "Blind Spot" in html


def test_pdf_bytes(client):
    from app import pdf

    pytest.importorskip("weasyprint")
    ed, user = _edition(client)
    data = pdf.render_pdf(pdf.render_html(ed, user))
    if data is None:
        pytest.skip("WeasyPrint system libraries unavailable")
    assert data.startswith(b"%PDF")
    assert len(data) > 5_000
