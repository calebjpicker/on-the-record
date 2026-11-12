#!/usr/bin/env python3
"""Build the static site from the JSON files under data/.

Usage:
    python3 scripts/build.py            # validate data and write _site/
    python3 scripts/build.py --check    # validate data only

Standard library only. No dependencies.
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "_site"

# Position a member has publicly taken on a candidate.
# "undeclared" is never stored: it is everyone with no entry.
POSITIONS = {
    "supports": "Supports",
    "opposes": "Will not support",
    "uncommitted": "Uncommitted",
}
POSITION_HELP = {
    "supports": "Has said they will support the candidate.",
    "opposes": "Has said in so many words that they will not support the candidate.",
    "uncommitted": "Has spoken about the contest without committing either way.",
}
BASES = {
    "quote": "Direct quote",
    "reported": "Reported by the source, no direct quote",
}
REQUIRED_DECLARATION_FIELDS = [
    "member", "role", "seat", "position", "candidate", "basis",
    "statement", "reported_on", "source_title", "source_url",
]

# Status of a member on a contest's roster. "pending" is a race that has not been called.
ROSTER_STATUSES = {"continuing", "re-elected", "elect", "pending"}
REQUIRED_ROSTER_FIELDS = ["name", "state", "party", "status", "source_url"]


class DataError(Exception):
    pass


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DataError(f"{path.relative_to(ROOT)}: invalid JSON: {exc}") from exc


def load_roster(contest, errors):
    """Load the roster of members who vote in a contest, when the contest names one."""
    rid = contest.get("electorate")
    if not rid:
        return None
    path = DATA / "rosters" / f"{rid}.json"
    rel = path.relative_to(ROOT)
    if not path.exists():
        errors.append(f"contests.json: {contest.get('id')}: roster {rel} not found")
        return None
    roster = load_json(path)
    for field in ("title", "as_of", "description", "members"):
        if not roster.get(field):
            errors.append(f"{rel}: missing {field}")
    try:
        date.fromisoformat(str(roster.get("as_of", "")))
    except ValueError:
        errors.append(f"{rel}: as_of must be YYYY-MM-DD")
    names = set()
    for i, m in enumerate(roster.get("members", [])):
        where = f"{rel}[{i}] {m.get('name', '?')}"
        for field in REQUIRED_ROSTER_FIELDS:
            if not str(m.get(field, "")).strip():
                errors.append(f"{where}: missing {field}")
        if m.get("status") not in ROSTER_STATUSES:
            errors.append(f"{where}: status must be one of {sorted(ROSTER_STATUSES)}")
        if not str(m.get("source_url", "")).startswith("https://"):
            errors.append(f"{where}: source_url must start with https://")
        if m.get("name") in names:
            errors.append(f"{where}: listed more than once")
        names.add(m.get("name"))
    for c in contest.get("candidates", []):
        if c.get("roster_name") not in names:
            errors.append(f"contests.json: {contest.get('id')}: candidate {c.get('id')!r} "
                          "needs a roster_name that matches the roster")
    return roster


def load_data():
    """Load and validate every contest and its declarations."""
    contests = load_json(DATA / "contests.json")
    errors = []
    seen_ids = set()
    for contest in contests:
        cid = contest.get("id", "")
        if not cid or cid in seen_ids:
            errors.append(f"contests.json: missing or duplicate id {cid!r}")
        seen_ids.add(cid)
        for field in ("title", "summary", "who_votes", "candidates", "stages", "sources"):
            if not contest.get(field):
                errors.append(f"contests.json: {cid}: missing {field}")
        candidate_ids = {c["id"] for c in contest.get("candidates", [])}
        roster = load_roster(contest, errors)
        roster_names = {m.get("name") for m in roster.get("members", [])} if roster else None

        path = DATA / "declarations" / f"{cid}.json"
        declarations = load_json(path) if path.exists() else []
        rel = path.relative_to(ROOT)
        seen_members = set()
        for i, d in enumerate(declarations):
            where = f"{rel}[{i}] {d.get('member', '?')}"
            for field in REQUIRED_DECLARATION_FIELDS:
                if not str(d.get(field, "")).strip():
                    errors.append(f"{where}: missing {field}")
            if d.get("position") not in POSITIONS:
                errors.append(f"{where}: position must be one of {sorted(POSITIONS)}")
            if d.get("basis") not in BASES:
                errors.append(f"{where}: basis must be one of {sorted(BASES)}")
            if d.get("candidate") not in candidate_ids:
                errors.append(f"{where}: unknown candidate {d.get('candidate')!r}")
            if roster_names is not None and d.get("member") not in roster_names:
                errors.append(f"{where}: not on the roster for this contest (names must match exactly)")
            if not str(d.get("source_url", "")).startswith("https://"):
                errors.append(f"{where}: source_url must start with https://")
            try:
                date.fromisoformat(str(d.get("reported_on", "")))
            except ValueError:
                errors.append(f"{where}: reported_on must be YYYY-MM-DD")
            key = (d.get("member"), d.get("candidate"))
            if key in seen_members:
                errors.append(f"{where}: more than one entry for this member and candidate")
            seen_members.add(key)
        contest["declarations"] = declarations
        contest["roster"] = roster
    if errors:
        raise DataError("\n".join(errors))
    return contests


CSS = """
:root{--ink:#14171F;--muted:#4B5563;--rule:#D5D8DE;--wash:#F3F4F6;--link:#3A2E7A;
--yes:#0B5A52;--no:#8A3A06;--no-bg:#FCEBDC;--unc:#3A2E7A;--unc-bg:#E9E6F5}
*{box-sizing:border-box}
body{margin:0;font-family:'Public Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
color:var(--ink);background:#fff;font-size:16px;line-height:1.5}
a{color:var(--link)}a:hover{color:#221A52}
.mono{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
.notice{background:var(--ink);color:#fff;font-size:14px;padding:10px 20px;text-align:center}
.notice a{color:#fff}
header.site{border-bottom:1px solid var(--rule)}
header.site .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;
gap:8px 24px;padding-top:12px;padding-bottom:12px}
.brand{font-weight:700;font-size:20px;color:var(--ink);text-decoration:none;padding:10px 0}
nav a{display:inline-block;padding:10px 0;margin-left:20px;color:var(--ink);font-size:15px}
main{padding:40px 0 56px}
h1{font-size:clamp(32px,5vw,46px);line-height:1.1;letter-spacing:-.02em;margin:8px 0 12px}
h2{font-size:24px;letter-spacing:-.01em;margin:40px 0 12px}
.lede{font-size:18px;color:var(--muted);max-width:720px;margin:0}
.kicker{font-size:14px;color:var(--muted)}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin-top:28px}
.fact{border-top:2px solid var(--ink);padding-top:12px}
.fact h3{margin:0 0 4px;font-size:16px}
.fact p{margin:0 0 4px;color:var(--muted);font-size:15px}
.tally{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:20px;
border:1px solid var(--rule);border-radius:8px;padding:24px;margin-top:28px}
.tally .label{font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:.06em}
.tally .num{font-size:48px;font-weight:700;line-height:1.05;letter-spacing:-.02em}
.tally .small{font-size:14px;color:var(--muted)}
.c-supports{color:var(--yes)}.c-opposes{color:var(--no)}.c-uncommitted{color:var(--unc)}.c-muted{color:var(--muted)}
.pill{display:inline-block;padding:4px 12px;border-radius:16px;font-size:14px;font-weight:600;white-space:nowrap}
.pill.supports{background:var(--yes);border:1px solid var(--yes);color:#fff}
.pill.opposes{background:var(--no-bg);border:1px solid var(--no);color:var(--no)}
.pill.uncommitted{background:var(--unc-bg);border:1px solid var(--unc);color:var(--unc)}
.scroll{overflow-x:auto;border:1px solid var(--rule);border-radius:8px}
table{border-collapse:collapse;width:100%;min-width:760px}
th{background:var(--wash);text-align:left;font-size:13px;text-transform:uppercase;letter-spacing:.06em;
color:var(--muted);padding:12px 16px}
td{border-top:1px solid var(--rule);padding:16px;vertical-align:top;font-size:15px}
td .name{font-weight:600}
td .sub{display:block;font-size:13px;color:var(--muted)}
.cards{border:1px solid var(--rule);border-radius:8px}
.card{display:block;padding:24px;color:var(--ink);text-decoration:none;border-top:1px solid var(--rule)}
.card:first-child{border-top:0}
.card:hover{background:var(--wash);color:var(--ink)}
.card .title{font-size:22px;font-weight:600;text-decoration:underline}
.card .counts{margin-top:8px;display:flex;flex-wrap:wrap;gap:6px 20px;font-size:15px;font-weight:600}
ul.plain{padding-left:20px;color:var(--muted)}
footer.site{border-top:1px solid var(--rule);background:var(--wash);font-size:14px;color:var(--muted)}
footer.site .wrap{padding-top:20px;padding-bottom:20px;display:flex;flex-wrap:wrap;gap:8px 24px;
justify-content:space-between}
.note{font-size:16px;color:var(--muted);max-width:720px;margin:0}
.roster{list-style:none;margin:20px 0 0;padding:0;display:grid;
grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px 24px}
.roster li{border-top:1px solid var(--rule);padding-top:8px;font-size:15px}
.roster .name{font-weight:600}
.roster .sub{display:block;font-size:13px;color:var(--muted)}
"""

REPO_URL = "https://github.com/calebjpicker/on-the-record"
FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500"
         "&family=Public+Sans:wght@400;500;600;700&display=swap")


def page(title: str, body: str, root: str) -> str:
    """Wrap page content in the shared layout. `root` is the relative path to the site root."""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="{FONTS}" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="notice">Early version. Every entry is a public statement linked to its source.
<a href="{REPO_URL}/issues">Report an error or add a statement</a>.</div>
<header class="site"><div class="wrap">
<a class="brand" href="{root}">On the Record</a>
<nav aria-label="Main"><a href="{root}">Contests</a><a href="{root}#how">How it works</a>
<a href="{REPO_URL}">Source and data</a></nav>
</div></header>
<main><div class="wrap">
{body}
</div></main>
<footer class="site"><div class="wrap">
<span>Open source. Data released under CC0. Not affiliated with Congress or any party.</span>
<span>Built {date.today().isoformat()}</span>
</div></footer>
</body>
</html>
"""


def counts(contest) -> dict:
    result = {key: 0 for key in POSITIONS}
    for d in contest["declarations"]:
        result[d["position"]] += 1
    return result


def undeclared(contest):
    """Roster members with no declaration, leaving out candidates and uncalled races.
    Returns None when the contest has no roster."""
    roster = contest.get("roster")
    if not roster:
        return None
    skip = {d["member"] for d in contest["declarations"]}
    skip |= {c.get("roster_name") for c in contest["candidates"]}
    return sorted((m for m in roster["members"] if m["status"] != "pending" and m["name"] not in skip),
                  key=lambda m: (m["state"], m["name"]))


def render_undeclared(contest, und) -> str:
    roster = contest["roster"]
    seat = roster.get("seat_title", "Member")
    noun = roster.get("member_noun", "members")
    pending = [m for m in roster["members"] if m["status"] == "pending"]
    seated = len(roster["members"]) - len(pending)
    submit = f"{REPO_URL}/issues/new?template=statement.yml"
    parts = [
        '<h2 id="undeclared">Undeclared</h2>',
        f'<p class="note">{len(und)} of the {seated} {escape(noun)} on the roster have no public statement '
        f'on file. Candidates are not counted. Know of a statement? <a href="{submit}">Send it with the '
        "source</a>.</p>",
        '<ul class="roster">',
    ]
    for m in und:
        tags = [f"{seat}-elect"] if m["status"] == "elect" else []
        if m.get("note"):
            tags.append(m["note"])
        parts.append(
            f'<li><span class="name">{escape(m["name"])}</span> '
            f'<span class="mono">{escape(m["party"])}-{escape(m["state"])}</span>'
            + "".join(f'<span class="sub">{escape(t)}</span>' for t in tags) + "</li>"
        )
    parts.append("</ul>")
    if pending:
        parts.append('<h3 style="margin-top:28px">Races not yet called</h3><ul class="plain">')
        for m in pending:
            parts.append(f'<li>{escape(m["state"])}: {escape(m["name"])} '
                         f'<span class="mono">{escape(m["party"])}</span>. '
                         f'{source_link("Source", m["source_url"])}</li>')
        parts.append("</ul>")
    parts.append(f'<p class="kicker">{escape(roster["description"])} Roster as of {escape(roster["as_of"])}. '
                 f'The source for each member is in the <a class="mono" href="../data/{contest["id"]}.json">'
                 "contest data</a>.</p>")
    return "\n".join(parts)


def source_link(title: str, url: str) -> str:
    return f'<a href="{escape(url, quote=True)}" rel="noopener">{escape(title)}</a>'


def render_contest(contest) -> str:
    tally = counts(contest)
    candidate_names = {c["id"]: c["name"] for c in contest["candidates"]}
    parts = [
        f'<div class="kicker mono">{escape(contest.get("congress", ""))}</div>',
        f'<h1>{escape(contest["title"])}</h1>',
        f'<p class="lede">{escape(contest["summary"])}</p>',
        '<div class="facts">',
        f'<div class="fact"><h3>Who votes</h3><p>{escape(contest["who_votes"])}</p>'
        f'<p>{escape(contest.get("electorate_note", ""))}</p></div>',
    ]
    for stage in contest["stages"]:
        parts.append(
            f'<div class="fact"><h3>{escape(stage["name"])}</h3>'
            f'<p>{escape(stage["when"])}</p><p>{escape(stage["ballot"])}</p></div>'
        )
    parts.append("</div>")

    parts.append("<h2>Declared candidates</h2><ul class=\"plain\">")
    for c in contest["candidates"]:
        parts.append(
            f'<li><strong style="color:var(--ink)">{escape(c["name"])}</strong> '
            f'<span class="mono">{escape(c["seat"])}</span>. {escape(c["note"])} '
            f'{source_link(c["source_title"], c["source_url"])}</li>'
        )
    parts.append("</ul>")

    parts.append('<div class="tally" role="group" aria-label="Tally of public statements">')
    for key, label in POSITIONS.items():
        parts.append(
            f'<div><div class="label c-{key}">{escape(label)}</div>'
            f'<div class="num">{tally[key]}</div></div>'
        )
    und = undeclared(contest)
    if und is None:
        parts.append(
            '<div><div class="label c-muted">Undeclared</div>'
            '<div class="num c-muted" style="font-size:22px;line-height:1.3;padding-top:8px">Everyone else</div>'
            '<div class="small">No public statement on file. Full roster coming.</div></div></div>'
        )
    else:
        parts.append(
            '<div><div class="label c-muted">Undeclared</div>'
            f'<div class="num c-muted">{len(und)}</div>'
            '<div class="small">No public statement on file. <a href="#undeclared">See who</a></div></div></div>'
        )

    parts.append("<h2>Public statements</h2>")
    if contest["declarations"]:
        order = list(POSITIONS)
        rows = sorted(contest["declarations"], key=lambda d: (order.index(d["position"]), d["member"]))
        parts.append('<div class="scroll"><table><thead><tr><th>Member</th><th>Position</th>'
                     "<th>Statement</th><th>Source</th></tr></thead><tbody>")
        for d in rows:
            parts.append(
                "<tr>"
                f'<td><span class="name">{escape(d["member"])}</span>'
                f'<span class="sub">{escape(d["role"])} · <span class="mono">{escape(d["seat"])}</span></span></td>'
                f'<td><span class="pill {d["position"]}">{escape(POSITIONS[d["position"]])}</span>'
                f'<span class="sub">on {escape(candidate_names[d["candidate"]])}</span></td>'
                f'<td>{escape(d["statement"])}</td>'
                f'<td>{source_link(d["source_title"], d["source_url"])}'
                f'<span class="sub">{escape(BASES[d["basis"]])}. Reported {escape(d["reported_on"])}</span></td>'
                "</tr>"
            )
        parts.append("</tbody></table></div>")
    else:
        parts.append('<p class="lede">No public statements on file yet.</p>')

    if und is not None:
        parts.append(render_undeclared(contest, und))

    parts.append("<h2>How entries are classified</h2><ul class=\"plain\">")
    for key, label in POSITIONS.items():
        parts.append(f"<li><strong style=\"color:var(--ink)\">{escape(label)}:</strong> {escape(POSITION_HELP[key])}</li>")
    parts.append("<li><strong style=\"color:var(--ink)\">Undeclared:</strong> No public statement on file. "
                 "This is the default for every member who votes in this contest.</li></ul>")

    parts.append("<h2>Sources for the facts above</h2><ul class=\"plain\">")
    for s in contest["sources"]:
        parts.append(f"<li>{source_link(s['title'], s['url'])}</li>")
    parts.append("</ul>")
    parts.append(f'<p class="kicker">Data for this page: <a class="mono" href="../data/{contest["id"]}.json">'
                 f'data/{contest["id"]}.json</a></p>')
    return "\n".join(parts)


def render_index(contests) -> str:
    parts = [
        "<h1>Where members of Congress say they stand, before the vote.</h1>",
        '<p class="lede">A public record of what senators and representatives have said about how they '
        "will vote. Anyone who has not said is listed as undeclared.</p>",
        "<h2>Contests</h2>",
        '<div class="cards">',
    ]
    for contest in contests:
        tally = counts(contest)
        first_stage = contest["stages"][0]
        und = undeclared(contest)
        parts.append(
            f'<a class="card" href="{contest["id"]}/">'
            f'<div class="kicker mono">{escape(contest.get("congress", ""))} · {escape(first_stage["when"])}</div>'
            f'<div class="title">{escape(contest["title"])}</div>'
            '<div class="counts">'
            + "".join(f'<span class="c-{k}">{tally[k]} {escape(POSITIONS[k].lower())}</span>' for k in POSITIONS)
            + (f'<span class="c-muted">{len(und)} undeclared</span>' if und is not None else "")
            + "</div></a>"
        )
    parts.append("</div>")
    parts.append(
        '<h2 id="how">How it works</h2><ul class="plain">'
        "<li>Each entry is something a member said in public, with a link to where it was reported.</li>"
        "<li>Entries are classified by the member's own words. A call for change that stops short of "
        "saying how the member will vote is listed as uncommitted.</li>"
        "<li>Private party votes are secret ballots, so these statements are the only public record. "
        "Where a vote is public, the recorded vote will be shown next to the statement afterward.</li>"
        f'<li>The data is plain files in a public repository. <a href="{REPO_URL}">Anyone can check it, '
        "correct it or add to it.</a></li></ul>"
    )
    return "\n".join(parts)


def build(contests) -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "data").mkdir(parents=True)
    (OUT / "index.html").write_text(
        page("On the Record", render_index(contests), "./"), encoding="utf-8")
    for contest in contests:
        folder = OUT / contest["id"]
        folder.mkdir()
        (folder / "index.html").write_text(
            page(f'{contest["title"]} | On the Record', render_contest(contest), "../"), encoding="utf-8")
        (OUT / "data" / f'{contest["id"]}.json').write_text(
            json.dumps(contest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "data" / "contests.json").write_text(
        json.dumps([{k: v for k, v in c.items() if k not in ("declarations", "roster")} for c in contests],
                   indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")


def main(argv: list[str]) -> int:
    try:
        contests = load_data()
    except DataError as exc:
        print("Data problems found:\n" + str(exc), file=sys.stderr)
        return 1
    total = sum(len(c["declarations"]) for c in contests)
    if "--check" in argv:
        print(f"OK: {len(contests)} contests, {total} declarations")
        return 0
    build(contests)
    print(f"Built {len(contests)} contests, {total} declarations into {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
