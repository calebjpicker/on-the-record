# Data

Everything here is plain JSON, dedicated to the public domain under CC0.

- `contests.json`: each contest, who votes in it, its stages and its declared candidates.
- `declarations/<contest-id>.json`: public statements by members who vote in that contest.

A member with no entry is **undeclared**. That is never written down; it is the default.

## Adding or correcting a statement

Add an object to the contest's file in `declarations/`:

| Field | Meaning |
|---|---|
| `member` | Name as commonly published. |
| `role` | `Senator`, `Senator-elect`, `Representative` or `Representative-elect`. |
| `seat` | Party and state, with district for the House: `D-MI`, `R-OH-4`, `I-VT`. |
| `position` | `supports`, `opposes` or `uncommitted`. See the rules below. |
| `candidate` | The `id` of a candidate listed for the contest in `contests.json`. |
| `basis` | `quote` if the source quotes the member directly, `reported` if it only describes the position. |
| `statement` | The member's words in quotation marks, or a neutral one-sentence description of what the source reports. |
| `reported_on` | Publication date of the source, `YYYY-MM-DD`. |
| `source_title` | Name of the outlet or site. |
| `source_url` | A public `https://` link to the source. |

One entry per member per candidate. To update a position, edit the entry; git history keeps the earlier version.

## Classification rules

- **`supports`**: the member has said they will support the candidate.
- **`opposes`**: the member has said in so many words that they will not support the candidate.
- **`uncommitted`**: the member has spoken about the contest without committing either way. A call for "new leadership" that stops short of saying how the member will vote goes here.

Classify by the member's own words, not by what a headline or commentator infers. When in doubt, use `uncommitted` and let the quote speak.

## Checking your change

```bash
python3 scripts/build.py --check
```

```bash
python3 scripts/build.py
```

The second command writes the site to `_site/`. Open `_site/index.html` in a browser.
