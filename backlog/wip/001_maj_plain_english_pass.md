# #001 — Plain-English pass over the archcheck launch post

**Status:** wip
**Priority:** maj
**Created:** 2026-07-16
**Started:** 2026-07-16
**Target:** `_posts/2026-07-15-i-built-archcheck-to-prove-agents-wreck-cpp-architecture.md`

## Why

The post is the launch article for `archcheck` and its main audience reads English as a second
language. Two problems, both measured rather than felt:

1. **Rare vocabulary.** A word-frequency pass (`wordfreq`, zipf < 3.5) flags words with a plain
   equivalent — `restated`, `disproportionately`, `contaminated`, `observational`. Each one costs
   a reader a beat for no gain.
2. **Undefined shorthand.** `settled weeks`, `god-header`, `trailing-include idiom`, `events` are
   used without a gloss. A reader who does not already know the study cannot follow the numbers.

A third class showed up while checking: sentences whose grammar hides the subject — *"generated
output grew faster than the human-review process recorded around it"* — which is the article's
central claim, stated in a way that has to be read twice.

## Rules of engagement

- Point edits only. Do not rewrite or regenerate the article.
- Do not touch: title, hook, section structure, tables, images, code blocks.
- Do not touch the author's deliberate phrasing: `wreck` in the title, `the corpus did not cooperate`.
- Keep domain terms even when rare: repo, commit, diff, merge, linter, boolean, coupling, baseline,
  corpus, drift, clone, header, include cycle.
- **Invent nothing.** Items marked VERIFY are checked against `blurman-ai/archcheck` first; a claim
  that cannot be traced is recorded as SKIPPED, not guessed.

## Verification done before editing (2026-07-16)

Source of truth: local `blurman-ai/archcheck` checkout at `~/projects/cpparch`.

| Claim in the post | Checked against | Result |
|---|---|---|
| "settled weeks", 2x / 1.7x / 1.4x | `experiments/adoption_event/study184_timeseries.csv`, pooled weekly rates, adopters | **Reproduced.** Weeks 4–12 after adoption vs weeks −12..−1: complexity **1.99**, boolean-flag **1.72**, new clones **1.42**, commits **1.38**. Windows starting at week 0 or 1 give 2.14 / 1.89 / 1.65 / 1.55 — so "settled" = the plateau after a ~3-week ramp, and the published numbers are the honest ones for that window. The headline estimator in `docs/research/all_endpoints_event_study.md` (exposure-weighted, ±12) reports 1.71 / 1.55 / 1.37 — same direction, different channel. |
| what an "event" is | `experiments/per_commit/run_worklist.py:86` (`categorize`) | `n_complexity` counts **`DRIFT.LOCAL_COMPLEXITY` violations**, one per function that grew — not one per commit. A commit can raise several. The proposed rewrite "commits that raise cognitive complexity" would have been **wrong**. |
| god-header definition | `src/rules/lakos_god_headers.cpp:29`, `docs/openwiki/index.md:84` | fan-in = `graph.predecessors(id).size()` = number of files that include the header **directly**; fires when fan-in > 50 (PCH names excluded). |
| RocksDB back edge + fan-in | `docs/findings/README.md` | Fix is one `class DB;` forward declaration in `multi_scan.h`; `db.h` fan-in is **110** (`Lakos.GodHeader` at threshold 50) — "hundreds" overstates it, use the real number. |
| folly mechanism | `docs/findings/README.md` | `Promise.h:490` includes `Future.h` back **at the bottom of the file, after `} // namespace folly`** — folly's idiom: declare the class, close the namespace, then include what the out-of-line bodies need. The back edge is `Future.h` itself, **not** an `-inl.h` header. |
| review numbers 45.8% → 58.1%, 49.2% → 48.0% | `docs/research/review_collapse.md:82-83` | Match. |
| 14-PR demo split | `gh pr list -R blurman-ai/archcheck-demo` | 14 PRs: P1–P5 copy-paste, S1–S4 partial copies, N1–N5 look-alikes → **9 fire, 5 stay silent**. The post already says 9 + 5 (fixed in `97b83c1`); the 5+5 wording in the request predates that commit. |

## Edits

Mandatory (reader loses the thread):

- [x] **M1** — "generated output grew faster than the human-review process recorded around it"
      → "teams generated code faster than they recorded reviews of it"
- [x] **M2** — "the back-edge is a removable forward declaration on a header with huge fan-in"
      → the back edge removable with one forward declaration, on a header **110 files include**
- [x] **M3** — 5+5 of 14 demo PRs. **SKIPPED** — already correct in the post (9 + 5).

Clarity:

- [x] **C1** — `simulation and HIL systems` → spell out hardware-in-the-loop on first use
- [x] **C2** — `In the settled weeks after adoption` → name the window (weeks 4–12)
- [x] **C3** — gloss "recall on those regressions"
- [x] **C4** — put the actor first in the 45.8% → 58.1% sentence
- [x] **C5** — "repeated what it claimed" → "repeated what the PR description claimed"
- [x] **C6** — "it marks it ambiguous and adds no edge; it does not guess" → two sentences, no semicolon
- [x] **C7** — folly's trailing-include idiom → state the mechanism
- [x] **C8** — "Review capacity does not scale with generation on its own."
- [x] **C9** — merge the two short sentences about reading meaning
- [x] **C10** — "introduced a new or grown include cycle" → "where an include cycle appeared or grew"
- [x] **C11** — "in the weeks around the moment it adopts agents" → "before and after it adopted agents"
- [x] **C12** — "cognitive-complexity events" → say what an event is (per function, not per commit)
- [x] **C13** — gloss god-header on first use

Vocabulary (zipf < 3.5 with a plain equivalent):

- [x] **V1** `not a refutation of their number` → `does not refute their number`
- [x] **V2** `restated the promise` → `repeated the promise`
- [x] **V3** `Squashed commits distort both attribution and change size` → `hide who wrote what and how much changed`
- [x] **V4** `The study is observational.` → `The study observes. It ran no experiment.`
- [x] **V5** `humans introduce disproportionately more` → `introduce more, even after matching commits by size`
- [x] **V6** — covered by C12
- [x] **V7** — merged into C6
- [x] **V8** `the human bucket is contaminated` → `the human bucket contains hidden AI code`

## Verification

```bash
pip install wordfreq --break-system-packages -q
python3 tools/freq_check.py <(article body: no front matter, no code blocks, no URLs)
```

Gate: no general-vocabulary word with zipf < 3.5 left in the output. Anything remaining is either
a domain term (added to `DOMAIN` with a reason) or gets replaced.

## Outcome (2026-07-16)

15 lines changed in the post. Title, hook, section structure, tables, images and code blocks
untouched.

| # | Verdict | Note |
|---|---|---|
| M1 | APPLIED | |
| M2 | MODIFIED | "hundreds of files" → **"110 other files"**. `docs/findings/README.md` reports `db.h` fan-in **110**; "hundreds" overstates a number we have exactly. Also "back-edge" → "back edge". |
| M3 | SKIPPED | Already correct in the post: it says 9 + 5, fixed in `97b83c1`. The demo repo has P1–P5 (copy-paste) + S1–S4 (partial copies) = 9 that fire, N1–N5 = 5 that stay silent. The 5+5 in the request predates that commit. |
| C1 | APPLIED | |
| C2 | MODIFIED | "settled weeks" → **"weeks 4 to 12"**, not "later weeks". The window is not vague — it is the plateau after a ~3-week ramp, and naming it both defines the term and lets a reader check the number. Reproduced from `study184_timeseries.csv` (see the verification table above). |
| C3 | APPLIED | |
| C4 | APPLIED | |
| C5 | APPLIED | |
| C6 | APPLIED | The post's only semicolon; it is gone. |
| C7 | MODIFIED | The proposed `-inl.h` wording is **factually wrong**: the back edge is `Future.h` itself, included at the bottom of `Promise.h:490` after `} // namespace folly` (`Promise-inl.h` sits next to it on line 491 but is not the cycle edge). Written by the mechanism instead: normal include one way, bottom-of-file include back, "where the function bodies need the full type". |
| C8 | APPLIED | |
| C9 | APPLIED | |
| C10 | APPLIED | Both places. |
| C11 | APPLIED | |
| C12 | MODIFIED | The proposed "commits that raise cognitive complexity" is **wrong**: `n_complexity` counts `DRIFT.LOCAL_COMPLEXITY` violations — **one per function that grew**, several possible per commit (`run_worklist.py:86`). Written as "warnings that a function grew more complex pile up about 2x faster per week". |
| C13 | APPLIED | Gloss from the rule itself: "(one that more than 50 files include directly)" — `fanIn = predecessors(id).size()`, threshold 50. |
| V1 | APPLIED | Still trips the gate at 3.14 — see below. |
| V2 | APPLIED | |
| V3 | APPLIED | |
| V4 | APPLIED | Two sentences, since C6 left no semicolon in the post. Still trips the gate at 3.32 — see below. |
| V5 | APPLIED | |
| V6 | APPLIED | Via C12 ("pile up"). |
| V7 | APPLIED | Merged into C6. |
| V8 | APPLIED | |

Outside the list, two words tripped the gate and had a plain equivalent that costs nothing:
`imitate` (3.29) → `match`, `unmarked` (3.24) → `AI use that nobody marked` (the latter fell out
of V8's sentence anyway).

### Frequency check

`tools/freq_check.py`, body with no front matter, code blocks or URLs.

Before — 23 words under zipf 3.5:

```
 0.00  archcheck-demo   0.00  blurman-ai    1.24  codebases      2.28  arxiv
 2.34  regressions      2.62  refutation    2.67  restated       2.97  idiom
 2.99  squashed         3.08  distort       3.14  observational  3.24  unmarked
 3.26  adopts           3.28  finder        3.29  freezes        3.29  imitate
 3.29  removable        3.30  disproportionately              3.31  flagged
 3.40  semantic         3.47  reviewer      3.47  rewrite        3.48  accumulate
```

After — 2:

```
 3.14    1  refute
 3.32    1  observes
```

The rest are either gone or listed in `SKIP` / `DOMAIN` with a one-line reason each
(`tools/freq_check.py`): proper nouns (`blurman-ai`, `archcheck-demo`, `arxiv`) and terms this
audience reads as vocabulary, not as rare words (`codebases`, `regressions`, `namespace`,
`squashed`, `finder`, `freezes`, `flagged`, `semantic`, `reviewer`, `rewrite`).

### Open for the author

`refute` (3.14) and `observes` (3.32) are the two words still under the bar — and both are the
**author's own target wording** from V1 and V4. Both are already improvements on what they
replaced (`refutation` 2.62, `observational` 3.14), so they were applied as written rather than
overridden. If the bar matters more than the phrasing:

- V1 — `does not refute` → `is not evidence against` (every word common). `disprove` is 2.93 and
  `contradict` 3.35, so both are worse.
- V4 — `The study observes.` → `The study observed what happened.` (`observed` is 4.39, present
  tense is what costs the points; the following sentence, "It ran no experiment", is past anyway).
