"""Newspaper PDF: Jinja HTML -> WeasyPrint. Returns None if WeasyPrint is not usable (caller serves HTML)."""
from __future__ import annotations

import base64
import io
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES = Path(__file__).parent / "templates"
_env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html"]))


def qr_data_uri(url: str) -> str | None:
    try:
        import qrcode
        import qrcode.image.svg

        img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=4, border=0)
        buf = io.BytesIO()
        img.save(buf)
        return "data:image/svg+xml;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def render_html(edition: dict, user: dict) -> str:
    items = edition["items"]
    qrs = {it["article_id"]: qr_data_uri(it["url"]) for it in items}
    letters = "abcdefgh"
    answers = ", ".join(f"{i + 1}{letters[q['answer']]}" for i, q in enumerate(edition.get("quiz", [])) if q.get("answer") is not None)
    return _env.get_template("paper.html").render(
        ed=edition, items=items, user=user, hero=items[0] if items else None, rest=items[1:], qrs=qrs,
        columns=edition.get("plan", {}).get("columns", 3), answers=answers, letters=letters,
    )


def render_pdf(html: str) -> bytes | None:
    try:
        from weasyprint import HTML

        return HTML(string=html, base_url=str(TEMPLATES)).write_pdf()
    except Exception:
        return None
