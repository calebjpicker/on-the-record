# On the Record (working title)

A public, open-source registry of how each member of Congress says they will vote on upcoming votes, before the vote happens.

For each upcoming vote, every senator or representative is listed with one of four states:

| State | Meaning |
|---|---|
| **Yes** | The office has stated the member will vote yes. |
| **No** | The office has stated the member will vote no. |
| **Undecided** | The office has answered, and the answer is that the member has not decided. |
| **Undeclared** | No answer on file. This is the default for all 535 members. |

Each entry carries an optional comment from the office, a source, a timestamp and a full public change history. After the vote, the recorded vote is shown next to what was declared.

**Status: design stage.** There are mockups and research, and no running code yet. Help is wanted; see [How to help](#how-to-help).

## Why

Positions on upcoming votes are scattered across press releases, social posts and one-off news "whip lists" compiled by hand. Nothing we found keeps a standing, open, per-member record that anyone can read, link to, embed or audit.

## How it works

1. **The schedule comes from official feeds.** Upcoming votes are pulled from the House and Senate floor schedules and Congress.gov.
2. **Offices answer by email.** Each office gets one email per vote. It replies from its official address with `YES`, `NO` or `UNDECIDED` on the first line and an optional comment after that. There is no account to create and no login.
3. **The public can add sourced statements.** Anyone can submit a link to a member's public statement. A reviewer checks it before it is published, and it is labeled as a public statement, not as an office reply.
4. **After the vote, the record is compared.** The recorded vote is pulled from the Clerk of the House and the Senate and shown beside the declaration.

### How an email reply is tied to an office

- The sender's address must be at `mail.house.gov` or `senate.gov` (senators' offices send from subdomains such as `name.senate.gov`).
- The message must carry a valid signature from that domain, checked on receipt.
- The reply must carry the one-time code from the request that was sent to that office's listed address.
- A receipt goes back to the office's listed address when the entry is published, so a mistaken or unauthorized entry can be withdrawn.
- The list of office addresses is a public file in this repository that anyone can correct.

## What the chamber rules say

We read the two governing documents directly. Neither one mentions a registry like this, and neither is a ruling on it. This is a reading by non-lawyers, not legal advice.

**Senate** — *U.S. Senate Internet Services and Technology Resources Usage Rules*, adopted by the Committee on Rules and Administration, November 9, 2015 (copy posted on a senator's site in 2026):

- Official business includes "the conveying of information to the public" (§1.8). Stating a vote position fits.
- An "Official Third-Party Website" is a non-Senate site "that a Senate Office uses for official business" (§1.6). Offices "may maintain an official account or official public profile" on one, and use of a site not on the Rules Committee's approved list "may be restricted" (§4.1–4.2). A site that asks offices to **create accounts** would fall under this. A plain email reply does not create an account or profile.
- "Communications in the normal course of Senate official business such as in direct response to a constituent ... and a news release to the communications media" stay permitted even in the 60 days before an election (§6.4).
- Senate resources may not be used for campaign, fundraising, commercial or promotional purposes (§2.2), and may not be used to impute unworthy motives to another senator (§2.5).

**House** — *Communications Standards Manual*, House Communications Standards Commission, effective May 2, 2024:

- Official business includes "the legislative process" and "Federal issues of public concern."
- "Direct responses to incoming correspondence on official business" and "Communications to the media" are exempt from the advisory-opinion requirement that applies to unsolicited mass communications. A one-to-one reply is also not a mass communication (500 or more recipients).
- **The line that cuts against us:** "Official communications resources may not be used by or on behalf of non-governmental organizations." An office answering a question is speaking for itself, but a cautious counsel could read recurring structured replies to an outside database differently.
- Offices may not endorse or promote non-governmental organizations, so the project should never ask an office to promote it.

**Not yet read:** the Members' Congressional Handbook (which governs House websites and social media accounts) and the Senate Ethics Manual. The definitive answer would be informal guidance from the Committee on House Administration and the Senate Rules Committee.

**What this means for the design**

- Email reply is the primary flow, because it needs no account.
- The project must be strictly nonpartisan and non-campaign: no scorecards, no endorsements, no calls to action against a member.
- Requests to offices should read like a press inquiry, which is the most established category in both documents.

## Data sources

| Need | Source | Notes |
|---|---|---|
| Members, IDs, official accounts | [`unitedstates/congress-legislators`](https://github.com/unitedstates/congress-legislators) | Public domain. |
| Bills and members | [Congress.gov API v3](https://github.com/LibraryOfCongress/api.congress.gov) | Free key, 5,000 requests per hour. |
| Upcoming House votes | Weekly XML under `docs.house.gov/billsthisweek/` | URL pattern is not formally documented. |
| Upcoming Senate votes | Floor schedule XML listed at `senate.gov/general/XML.htm` | Not yet inspected. |
| Recorded House votes | Congress.gov `house-vote` endpoints (beta, 2023 onward) or Clerk XML | |
| Recorded Senate votes | Roll call XML on senate.gov | No Senate vote endpoint in the Congress.gov API that we could find. |

The ProPublica Congress API and the GovTrack API are no longer available.

## Proposed principles

- Nonpartisan. No ratings, endorsements or advocacy.
- Every entry has a source and a public history. Nothing is silently changed or removed.
- Code is open source. Data is public domain (CC0).
- The data lives as plain files in this repository, so every change is a reviewable commit.

## How to help

- **Congressional staff or former staff:** tell us whether an office would answer a request like this, and who in the office would decide.
- **Ethics and administration counsel:** check our reading of the chamber rules above.
- **Email engineers:** test whether House and Senate office mail carries a verifiable DKIM signature, and design the inbound verification.
- **Civic-data developers:** build the schedule ingest for the House and Senate feeds and the recorded-vote comparison.
- **Designers and writers:** review the mockups and the wording of the request email for neutrality.
- **Anyone:** help compile the public list of each office's press contact address.

## Open questions

- Which votes are covered at launch, and who chooses them?
- How are public-statement submissions reviewed, and by whom?
- What organization, if any, operates the site and its mailboxes?
- What is the project's name and domain?

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how work is organized: one branch per change, each in its own git worktree, merged through a pull request.

## License

- **Code:** MIT. See [LICENSE](LICENSE).
- **Data:** public domain under CC0 1.0. See [LICENSE-DATA.md](LICENSE-DATA.md).
