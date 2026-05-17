#!/usr/bin/env python3
"""Extract per-episode lesson plans from index.html into lessons/*.md and lessons/*.html.

Run from the repo root:
    python scripts/extract_lessons.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_HTML = REPO_ROOT / "index.html"
OUT_DIR = REPO_ROOT / "lessons"

STANDALONE_CSS = """\
:root {
  --blueprint: #0d1b2a;
  --blueprint-mid: #1b2838;
  --copper: #c87533;
  --copper-bright: #e8943b;
  --copper-dim: #8a5a2a;
  --steel: #8899aa;
  --chalk: #d4dce6;
  --chalk-dim: rgba(212, 220, 230, 0.6);
  --white: #f0f4f8;
  --green-pass: #4caf50;
  --red-fail: #c0392b;
  --yellow-plausible: #d4a017;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Source Sans Pro', system-ui, -apple-system, sans-serif;
  background: var(--blueprint);
  color: var(--chalk);
  line-height: 1.7;
  padding: 2rem;
  max-width: 820px;
  margin: 0 auto;
}
header { border-bottom: 1px solid rgba(200, 117, 51, 0.25); padding-bottom: 1rem; margin-bottom: 1.5rem; }
.ep-num {
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
  font-size: 0.7rem; letter-spacing: 0.15em; color: var(--copper); text-transform: uppercase;
}
h1 {
  font-family: 'Merriweather', Georgia, serif;
  font-size: 1.8rem; color: var(--white); margin: 0.5rem 0 0.75rem;
}
.brief { color: var(--chalk-dim); font-style: italic; }
.lesson-plan { margin-top: 1.5rem; }
.lesson-plan-header {
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
  font-size: 0.7rem; font-weight: 700; letter-spacing: 0.2em;
  color: var(--copper); text-transform: uppercase;
  margin-bottom: 0.75rem; padding-bottom: 0.4rem;
  border-bottom: 1px solid rgba(200, 117, 51, 0.15);
}
.lesson-row {
  display: grid; grid-template-columns: 90px 1fr; gap: 1rem;
  padding: 0.6rem 0; border-bottom: 1px solid rgba(136, 153, 170, 0.08);
  align-items: baseline;
}
.lesson-row:last-child { border-bottom: none; }
.lesson-time {
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
  font-size: 0.75rem; font-weight: 700; color: var(--copper);
}
.lesson-desc strong { color: var(--white); }
.time-hack {
  display: grid; grid-template-columns: 90px 1fr auto; gap: 1rem;
  padding: 0.75rem; margin: 0.5rem 0;
  background: rgba(13, 27, 42, 0.6); border-left: 3px solid var(--copper);
  align-items: center;
}
.time-hack-stamp { font-family: 'IBM Plex Mono', ui-monospace, monospace; font-size: 0.8rem; font-weight: 700; color: var(--copper-bright); }
.time-hack-desc { font-size: 0.95rem; }
.time-hack-verdict {
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
  font-size: 0.6rem; font-weight: 700; letter-spacing: 0.1em;
  padding: 0.2rem 0.5rem; text-transform: uppercase;
}
.time-hack-verdict.pass { border: 1px solid var(--green-pass); color: var(--green-pass); }
.time-hack-verdict.fail { border: 1px solid var(--red-fail); color: var(--red-fail); }
.time-hack-verdict.plausible { border: 1px solid var(--yellow-plausible); color: var(--yellow-plausible); }
.lesson-standards { margin-top: 1.5rem; padding-top: 0.75rem; border-top: 1px solid rgba(136, 153, 170, 0.1); }
.lesson-standards-label {
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
  font-size: 0.6rem; font-weight: 700; letter-spacing: 0.2em;
  color: var(--steel); text-transform: uppercase; margin-bottom: 0.5rem;
}
.standard-tag {
  display: inline-block;
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
  font-size: 0.65rem; font-weight: 700;
  padding: 0.2rem 0.5rem; margin: 0.15rem 0.25rem 0.15rem 0;
  border: 1px solid var(--steel); color: var(--steel);
}
.themes { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.75rem; margin-top: 1rem; }
.theme-card {
  background: rgba(13, 27, 42, 0.5);
  border: 1px solid rgba(136, 153, 170, 0.1); padding: 1rem;
}
.theme-card h4 { font-family: 'Merriweather', Georgia, serif; font-size: 1rem; color: var(--white); margin-bottom: 0.4rem; }
.theme-card p { font-size: 0.9rem; color: var(--chalk-dim); }
footer { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(136, 153, 170, 0.1); font-size: 0.8rem; color: var(--chalk-dim); }
footer a { color: var(--copper); text-decoration: none; }
"""


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def ep_key(ep_num: str) -> str:
    """Normalize 'S01 E01' -> 'S01E01'."""
    return re.sub(r"\s+", "", ep_num)


def find_named_block(card: Tag, header_prefix: str) -> Tag | None:
    """Find a div.lesson-plan whose .lesson-plan-header text starts with prefix."""
    for lp in card.select("div.lesson-plan"):
        header = lp.select_one(".lesson-plan-header")
        if header and header.get_text(strip=True).startswith(header_prefix):
            return lp
    return None


def extract_lesson_rows(block: Tag) -> list[tuple[str, str]]:
    rows = []
    for row in block.select(".lesson-row"):
        time_el = row.select_one(".lesson-time")
        desc_el = row.select_one(".lesson-desc")
        if not time_el or not desc_el:
            continue
        rows.append((time_el.get_text(strip=True), desc_el))
    return rows


def extract_time_hacks(block: Tag) -> list[tuple[str, str, str]]:
    hacks = []
    for hack in block.select(".time-hack"):
        stamp = hack.select_one(".time-hack-stamp")
        desc = hack.select_one(".time-hack-desc")
        verdict = hack.select_one(".time-hack-verdict")
        if not stamp or not desc:
            continue
        verdict_text = verdict.get_text(strip=True) if verdict else ""
        verdict_cls = ""
        if verdict and verdict.get("class"):
            cls = [c for c in verdict.get("class", []) if c != "time-hack-verdict"]
            verdict_cls = cls[0] if cls else ""
        hacks.append((stamp.get_text(strip=True), desc.get_text(" ", strip=True), verdict_text, verdict_cls))
    return hacks


def extract_standards(card: Tag) -> tuple[str, list[str]]:
    block = card.select_one(".lesson-standards")
    if not block:
        return "", []
    label_el = block.select_one(".lesson-standards-label")
    label = label_el.get_text(strip=True) if label_el else "Aligned Standards"
    tags = [t.get_text(strip=True) for t in block.select(".standard-tag")]
    return label, tags


def extract_themes(card: Tag) -> list[tuple[str, str]]:
    themes = []
    for tc in card.select(".theme-card"):
        h = tc.find(["h4", "h3"])
        p = tc.find("p")
        if h and p:
            themes.append((h.get_text(strip=True), p.get_text(" ", strip=True)))
    return themes


def desc_to_markdown(desc_el: Tag) -> str:
    """Convert a lesson-desc element to inline Markdown, preserving <strong>."""
    parts: list[str] = []
    for node in desc_el.children:
        if isinstance(node, NavigableString):
            parts.append(str(node))
        elif isinstance(node, Tag):
            if node.name == "strong":
                parts.append(f"**{node.get_text(' ', strip=True)}**")
            elif node.name == "em":
                parts.append(f"*{node.get_text(' ', strip=True)}*")
            else:
                parts.append(node.get_text(" ", strip=True))
    text = "".join(parts)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def desc_to_html(desc_el: Tag) -> str:
    """Return inner HTML of a description element (preserves <strong>, <em>)."""
    return desc_el.decode_contents().strip()


def render_markdown(card_data: dict) -> str:
    lines: list[str] = []
    lines.append(f"# {card_data['ep_num']} — {card_data['title']}")
    lines.append("")
    if card_data.get("brief"):
        lines.append(f"> {card_data['brief']}")
        lines.append("")
    lines.append(f"## Lesson Plan: {card_data['lesson_title']}")
    lines.append("")
    for time, desc_el in card_data["lesson_rows"]:
        lines.append(f"- **{time}** — {desc_to_markdown(desc_el)}")
    lines.append("")
    if card_data["time_hacks"]:
        lines.append("## Time Hacks — Clips to Show in Class")
        lines.append("")
        lines.append("| Timestamp | Clip | Verdict |")
        lines.append("|---|---|---|")
        for stamp, desc, verdict, _ in card_data["time_hacks"]:
            verdict_md = f"**{verdict}**" if verdict else ""
            lines.append(f"| `{stamp}` | {desc} | {verdict_md} |")
        lines.append("")
    if card_data["standards"][1]:
        label, tags = card_data["standards"]
        lines.append(f"## {label}")
        lines.append("")
        for tag in tags:
            lines.append(f"- {tag}")
        lines.append("")
    if card_data["themes"]:
        lines.append("## Themes")
        lines.append("")
        for name, desc in card_data["themes"]:
            lines.append(f"- **{name}** — {desc}")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("Extracted from [`index.html`](../index.html). Regenerate with `python scripts/extract_lessons.py`.")
    lines.append("")
    return "\n".join(lines)


def render_html(card_data: dict) -> str:
    parts: list[str] = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="en"><head>')
    parts.append('<meta charset="UTF-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    parts.append(f"<title>{card_data['ep_num']} — {card_data['title']} | MacGyver Office Hours</title>")
    parts.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
    parts.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    parts.append('<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Merriweather:wght@400;700;900&family=Source+Sans+Pro:wght@400;600;700&display=swap" rel="stylesheet">')
    parts.append(f"<style>\n{STANDALONE_CSS}</style>")
    parts.append("</head><body>")
    parts.append("<header>")
    parts.append(f'<div class="ep-num">{card_data["ep_num"]}</div>')
    parts.append(f"<h1>{card_data['title']}</h1>")
    if card_data.get("brief"):
        parts.append(f'<p class="brief">{card_data["brief"]}</p>')
    parts.append("</header>")

    parts.append('<section class="lesson-plan">')
    parts.append(f'<div class="lesson-plan-header">Lesson Plan: {card_data["lesson_title"]}</div>')
    for time, desc_el in card_data["lesson_rows"]:
        parts.append('<div class="lesson-row">')
        parts.append(f'<span class="lesson-time">{time}</span>')
        parts.append(f'<span class="lesson-desc">{desc_to_html(desc_el)}</span>')
        parts.append("</div>")
    parts.append("</section>")

    if card_data["time_hacks"]:
        parts.append('<section class="lesson-plan">')
        parts.append('<div class="lesson-plan-header">Time Hacks — Clips to Show in Class</div>')
        for stamp, desc, verdict, verdict_cls in card_data["time_hacks"]:
            parts.append('<div class="time-hack">')
            parts.append(f'<span class="time-hack-stamp">{stamp}</span>')
            parts.append(f'<span class="time-hack-desc">{desc}</span>')
            if verdict:
                cls = f"time-hack-verdict {verdict_cls}".strip()
                parts.append(f'<span class="{cls}">{verdict}</span>')
            parts.append("</div>")
        parts.append("</section>")

    if card_data["standards"][1]:
        label, tags = card_data["standards"]
        parts.append('<section class="lesson-standards">')
        parts.append(f'<div class="lesson-standards-label">{label}</div>')
        for tag in tags:
            parts.append(f'<span class="standard-tag">{tag}</span>')
        parts.append("</section>")

    if card_data["themes"]:
        parts.append('<section><div class="lesson-plan-header" style="margin-top:1.5rem">Themes</div>')
        parts.append('<div class="themes">')
        for name, desc in card_data["themes"]:
            parts.append(f'<div class="theme-card"><h4>{name}</h4><p>{desc}</p></div>')
        parts.append("</div></section>")

    parts.append('<footer>Extracted from <a href="../index.html">index.html</a>. Regenerate with <code>python scripts/extract_lessons.py</code>.</footer>')
    parts.append("</body></html>")
    return "\n".join(parts) + "\n"


def main() -> int:
    if not SRC_HTML.exists():
        print(f"error: {SRC_HTML} not found", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(exist_ok=True)
    soup = BeautifulSoup(SRC_HTML.read_text(encoding="utf-8"), "html.parser")

    extracted: list[tuple[str, str]] = []
    skipped: list[str] = []

    for card in soup.select("div.episode-card"):
        ep_num_el = card.select_one(".card-ep-num")
        title_el = card.select_one(".card-title")
        brief_el = card.select_one(".card-brief")
        if not ep_num_el or not title_el:
            continue
        ep_num = ep_num_el.get_text(" ", strip=True)
        title = title_el.get_text(strip=True)
        brief = brief_el.get_text(" ", strip=True) if brief_el else ""

        lesson_block = find_named_block(card, "Lesson Plan:")
        if not lesson_block:
            skipped.append(f"{ep_key(ep_num)} — {title}")
            continue

        header_text = lesson_block.select_one(".lesson-plan-header").get_text(strip=True)
        lesson_title = header_text.split(":", 1)[1].strip() if ":" in header_text else header_text

        time_hack_block = find_named_block(card, "Time Hacks")

        card_data = {
            "ep_num": ep_key(ep_num),
            "title": title,
            "brief": brief,
            "lesson_title": lesson_title,
            "lesson_rows": extract_lesson_rows(lesson_block),
            "time_hacks": extract_time_hacks(time_hack_block) if time_hack_block else [],
            "standards": extract_standards(card),
            "themes": extract_themes(card),
        }

        slug = slugify(title)
        base = f"{card_data['ep_num']}-{slug}"
        md_path = OUT_DIR / f"{base}.md"
        html_path = OUT_DIR / f"{base}.html"
        md_path.write_text(render_markdown(card_data), encoding="utf-8")
        html_path.write_text(render_html(card_data), encoding="utf-8")
        extracted.append((card_data["ep_num"], title))

    print(f"Extracted: {len(extracted)} lesson plan(s)")
    for ep, title in extracted:
        print(f"  {ep}  {title}")
    if skipped:
        print(f"\nSkipped (no lesson plan block): {len(skipped)}")
        for s in skipped:
            print(f"  {s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
