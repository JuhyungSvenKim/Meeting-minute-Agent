"""Export meeting summary to PDF / Markdown / TXT."""
from __future__ import annotations

import io
import re
from datetime import datetime
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def _safe_filename(title: str) -> str:
    base = re.sub(r"[^\w\-가-힣 ]+", "", title or "meeting").strip().replace(" ", "_")
    return base or "meeting"


def _content(summary: dict[str, Any]) -> dict[str, Any]:
    c = summary.get("content") or {}
    return {
        "title": c.get("title") or "",
        "attendees": c.get("attendees") or [],
        "summary": c.get("summary") or "",
        "key_points": c.get("key_points") or [],
        "decisions": c.get("decisions") or [],
        "action_items": c.get("action_items") or [],
    }


def _meeting_date_str(meeting: dict[str, Any]) -> str:
    raw = meeting.get("meeting_date") or meeting.get("created_at")
    if not raw:
        return ""
    try:
        if isinstance(raw, str):
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        else:
            dt = raw
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:  # noqa: BLE001
        return str(raw)


# ----------------------------- Markdown -----------------------------
def _to_markdown(meeting: dict[str, Any], summary: dict[str, Any]) -> str:
    c = _content(summary)
    title = c["title"] or meeting.get("title") or "Meeting Minutes"
    date = _meeting_date_str(meeting)
    parts = [f"# {title}", ""]
    if date:
        parts.append(f"- **Date**: {date}")
    if c["attendees"]:
        parts.append(f"- **Attendees**: {', '.join(c['attendees'])}")
    parts.append(f"- **LLM**: {summary.get('llm_provider', '')}")
    parts.append("")
    if c["summary"]:
        parts += ["## Summary", "", c["summary"], ""]
    if c["key_points"]:
        parts += ["## Key Points", ""]
        parts += [f"- {p}" for p in c["key_points"]]
        parts.append("")
    if c["decisions"]:
        parts += ["## Decisions", ""]
        parts += [f"- {d}" for d in c["decisions"]]
        parts.append("")
    if c["action_items"]:
        parts += ["## Action Items", ""]
        for a in c["action_items"]:
            owner = a.get("owner") or "-"
            due = a.get("due_date") or "-"
            parts.append(f"- **{a.get('title', '')}** _(owner: {owner}, due: {due})_")
        parts.append("")
    return "\n".join(parts)


# ----------------------------- TXT -----------------------------
def _to_txt(meeting: dict[str, Any], summary: dict[str, Any]) -> str:
    c = _content(summary)
    title = c["title"] or meeting.get("title") or "Meeting Minutes"
    date = _meeting_date_str(meeting)
    out = [title, "=" * len(title), ""]
    if date:
        out.append(f"Date: {date}")
    if c["attendees"]:
        out.append(f"Attendees: {', '.join(c['attendees'])}")
    out.append(f"LLM: {summary.get('llm_provider', '')}")
    out.append("")
    if c["summary"]:
        out += ["[Summary]", c["summary"], ""]
    if c["key_points"]:
        out.append("[Key Points]")
        out += [f"  - {p}" for p in c["key_points"]]
        out.append("")
    if c["decisions"]:
        out.append("[Decisions]")
        out += [f"  - {d}" for d in c["decisions"]]
        out.append("")
    if c["action_items"]:
        out.append("[Action Items]")
        for a in c["action_items"]:
            owner = a.get("owner") or "-"
            due = a.get("due_date") or "-"
            out.append(f"  - {a.get('title', '')} (owner: {owner}, due: {due})")
        out.append("")
    return "\n".join(out)


# ----------------------------- PDF -----------------------------
def _to_pdf(meeting: dict[str, Any], summary: dict[str, Any]) -> bytes:
    c = _content(summary)
    title = c["title"] or meeting.get("title") or "Meeting Minutes"
    date = _meeting_date_str(meeting)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=18, spaceAfter=10)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13, spaceAfter=6)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10.5, leading=14)
    meta = ParagraphStyle("meta", parent=body, textColor="#555555", fontSize=9.5)

    story: list = [Paragraph(title, h1)]
    meta_bits = []
    if date:
        meta_bits.append(f"Date: {date}")
    if c["attendees"]:
        meta_bits.append(f"Attendees: {', '.join(c['attendees'])}")
    meta_bits.append(f"LLM: {summary.get('llm_provider', '')}")
    story.append(Paragraph(" &nbsp;|&nbsp; ".join(meta_bits), meta))
    story.append(Spacer(1, 6))

    if c["summary"]:
        story += [Paragraph("Summary", h2), Paragraph(c["summary"], body), Spacer(1, 6)]

    def _bullets(items: list[str]):
        return ListFlowable(
            [ListItem(Paragraph(i, body)) for i in items],
            bulletType="bullet",
            leftIndent=12,
        )

    if c["key_points"]:
        story += [Paragraph("Key Points", h2), _bullets(c["key_points"]), Spacer(1, 6)]
    if c["decisions"]:
        story += [Paragraph("Decisions", h2), _bullets(c["decisions"]), Spacer(1, 6)]
    if c["action_items"]:
        items = []
        for a in c["action_items"]:
            owner = a.get("owner") or "-"
            due = a.get("due_date") or "-"
            items.append(f"<b>{a.get('title', '')}</b> &nbsp;<i>(owner: {owner}, due: {due})</i>")
        story += [Paragraph("Action Items", h2), _bullets(items)]

    doc.build(story)
    return buf.getvalue()


def export_summary(
    meeting: dict[str, Any], summary: dict[str, Any], fmt: str
) -> tuple[bytes, str]:
    title = (summary.get("content") or {}).get("title") or meeting.get("title") or "meeting"
    base = _safe_filename(title)
    if fmt == "md":
        return _to_markdown(meeting, summary).encode("utf-8"), f"{base}.md"
    if fmt == "txt":
        return _to_txt(meeting, summary).encode("utf-8"), f"{base}.txt"
    if fmt == "pdf":
        return _to_pdf(meeting, summary), f"{base}.pdf"
    raise ValueError(f"Unsupported format: {fmt}")
