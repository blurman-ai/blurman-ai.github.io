# #002 — A living article about clean rooms for coding agents

**Status:** completed
**Priority:** maj
**Created:** 2026-10-22
**Started:** 2026-10-22
**Target:** `_posts/2026-10-22-a-clean-room-for-coding-agents.md`

## Request

Write an English article for Sergey's existing site about clean-room development: its history,
examples, and principles. Use the author's LinkedIn post supplied on 2026-10-22 as the
starting point. Keep one article that can grow through later additions.

## Sources and scope

- Author's supplied post: the failed attempt, four patches in one day, state reconstructed
  across seven tables, behavior cards, and the ten rules. These are the author's account,
  not an independently measured comparison of agents or implementations.
- Phoenix Technologies, *System BIOS for IBM PC/XT/AT Computers and Compatibles*,
  ISBN 0-201-51806-6, Neil J. Colvin's foreword, pp. xviii–xxi. Primary account of the
  May 1984 BIOS and separation between engineers studying its behavior and engineers
  implementing it. Read through the searchable copy:
  https://dokumen.pub/system-bios-for-ibm-pc-xt-at-computers-and-compatibles-the-complete-guide-to-rom-based-system-software-2nbsped-9780201518061-0201518066.html
- Existing site uses Jekyll/Minima, English posts and dated permalinks. Reuse these.
- Prior work: historical clean-room separation already supplies the process. The ten
  architecture rules come from the author; do not attribute them to Phoenix or claim
  that Phoenix invented specification-driven development.
- Today's internal audit, dated 2026-10-22: used only to
  refine general principles about decision ownership, contract declarations, structured
  meaning, frontend state, and recovery from waits. The author explicitly excluded
  reporting compliance or violations. No audit findings, counts, or internal paths
  appear in the article.

## Editorial decisions

- Use "clean room" for the development process and "new implementation" for its output.
  On 2026-10-22 the author questioned "contour" as an English term; removed the literal
  translation and the invented definition from the unpublished draft.
- Preserve the supplied first-person incident; make no new claim about the live product.
- Mark the transition table and behavior card as illustrative examples, not recovered
  production artifacts. State concurrency and failed-persistence limits explicitly.
- Keep a stable `/clean-room/` URL, a visible revision date, and a dated update log.
  The earlier `/clean-contour/` preview was never published and needs no redirect.
- Future changes name the added evidence and do not silently replace published claims.
- Follow-up request on 2026-10-22: add concrete examples. Each of the ten principles
  now has an illustrative situation, an application of the rule, and a way to verify
  the resulting behavior. These are teaching examples, not additional incident claims.

## Verification and outcome

- APPLIED: English article with ten principles, Phoenix history, behavior card, state
  machine example, frontend mapping, practical checks, and article history.
- APPLIED: ten additional examples, one per principle: persisted reviewer verdict,
  shared assessment policy, parser recovery, late provider response, package boundaries,
  rate-limit reason codes, failed commit, kind dispatch, migration adapter, and the
  architecture proposal after three patches. Each includes an observable check.
- APPLIED: audit-derived clarification that one state setter is insufficient unless
  transition decisions have one owner too. Included contract types, structured reason
  metadata, explicit missing-content values, and recovery owners for waiting states.
- MODIFIED: the supplied "failure on failed write" rule explains that an unavailable
  database cannot record its own failure; stop dependent work and use recovery instead.
- SKIPPED by author instruction: compliance findings, violation counts, and audit verdicts.
- Primary historical text verified in the searchable reproduction of the Phoenix book;
  the linked mirror serves a browser challenge to direct curl requests.
- PASS: `BUNDLE_PATH=/tmp/blekher-blog-gems BUNDLE_FROZEN=true bundle3.2 exec jekyll build --trace`.
  Kept the existing Gemfile and lockfile unchanged. Missing Ruby headers were extracted
  under `/tmp` for dependency compilation; no system package installation was needed.
- PASS: rendered `/clean-room/index.html`, all ten rule headings, four tables,
  resolution of every local article link, homepage listing, and feed entry.
- PASS: English-only content, stable permalink, and no internal audit references in
  the article. `git diff --check` passed.
- Browser QA unavailable: CUA returned "No browser is available". No visual review claimed.
- Local preview: `http://127.0.0.1:4187/clean-room/` while the preview process runs.
## Rewrite for publication, 2026-10-22

Request: rules as short and direct as in the LinkedIn post, examples visually separated
from the main text, no reasoning paragraphs.

- APPLIED: the ten rule statements follow the LinkedIn wording; each rule is a framed block,
  each example a separate "Example" block with a "Check" line.
- APPLIED: a numbered summary of the ten rules after the introduction, linked to the rules.
- APPLIED: a five-step figure of who sees what in a clean room; the behavior card and the
  state machine are set as examples.
- APPLIED: `assets/main.scss` overrides minima's stylesheet; it imports `minima` and adds
  only classes used by this post (`rules-summary`, `rule`, `example`, `check`, `flow`).
  On a phone the figure stacks vertically and tables scroll inside their own box.
- REMOVED: the paragraphs explaining the rules, the event-sourcing note, the caveats
  "illustrative, not a production specification" and "not a measured optimum", the
  closing summary, and the claim that the examples are not drawn from a real product.
- MODIFIED: the Phoenix source is a book citation with ISBN; the link to a reproduction
  on dokumen.pub is removed.
- PASS: `jekyll build` with the locked gems. Screenshots in Chrome at 1100 px and 390 px;
  page width at 390 px equals the viewport.
- Published: branch merged into `main` (the Pages source), URL `/clean-room/`.
- APPLIED, same day, on the author's request: fourteen rules, matching the source rule set
  (baseline `template/rules/16-clean-contour.md`, 14 principles). Added: parts accepted
  separately, every check has failed once, the screen draws what the server returned,
  the outcome does not depend on the order of responses; each with an example and a check.
  "Three failed patches" moved to rule 14.
- APPLIED, same day: rule 14 "the server decides what is allowed" (baseline principle 15,
  an internal issue), "three failed patches" is rule 15. A paragraph after the opening
  story from the author's team chat of 22.10.2026: a developer expected the model to know
  these principles already. The developer is not named.

## Rewrite to match Habr, 2026-10-30

Request (2026-10-30): bring the English post in line with the author's Habr article, in plain
English. Habr's jokes stay out. Existing examples stay; the new example under rule 9 and the
sample card are teaching examples. Not committed or published.

Sources: https://habr.com/ru/articles/1101314/ (source of truth), `backlog/wip/001_maj_plain_english_pass.md`.

- APPLIED: rewrite in the working tree: two projects, analyst and implementer, four ways the
  old code is kept away, migration steps, rule order and numbers as on Habr, antigoal rule as a
  separate section, ub-mode, weak-model measurement.
- FIXED against Habr: "I rewrote" → "We rewrote" and "the same way" → "in a similar way" in the
  excerpt; "I call" → "Claude and I called" a clean room; Phoenix "a programmer" → "others";
  "expired lock" → "lost lock" (rule 7); "real defect" → "the defect it checks" (rule 11);
  rule 14 now says that the order of responses does not change the result; `cancel_reason`
  glossed as the reason for cancellation; "Check for a finished order" → "Completion check";
  removed "Phoenix did it for legal reasons", which neither Habr nor the earlier post says;
  added the card's missing line "What confirms it".
- MATCHED, no change: 2 of 3 calls HTTP 500; 21 negation places; 2 + 3 + 2 days; three days on
  the second project; six repositories; 36 runs and 36/31/25/18; 3 of 3 vs 0 of 3; four
  then five `cancel_reason` checks; all fifteen rules in order.
- APPLIED: 19 plain-English point edits. `tools/freq_check.py` was not changed; remaining words
  under zipf 3.5 are names and technical terms, plus `hallucinate`, `negation` and `foreword`.
- PASS: `jekyll build --trace` with locked gems in a temporary path. Gemfile and
  lockfile unchanged. Ruby headers were extracted to a temporary path; no system packages.
- PASS: 15 rule anchors plus `#antigoal`, all 16 summary links resolve, 6 tables, diff block with
  removed and added lines, `post_url` resolves, no "contour" in the page. `git diff --check` clean.
- PASS: headless Chrome at 390 px: page width equals the viewport, tables scroll inside their box.
