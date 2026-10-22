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
- Today's audit, `dgtlU/tmp/audit-patches/AUDIT.md`, dated 2026-10-22: used only to
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
