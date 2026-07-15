---
layout: post
title: "I built archcheck to prove coding agents wreck C++ architecture. 484,500 commits later, I couldn't."
date: 2026-07-15
---

I build simulation and HIL systems in C++, and by early 2026 most of the new code around me came from coding agents. I expected their failure mode to be structural. Agents imitate nearby code well, but constraints that span files and modules are easy to lose across a long context. The result should have been more include cycles, god-headers, copy-paste, cross-module coupling.

I built a tool to measure exactly those regressions per commit, ran it across a large corpus to prove the point, and the corpus did not cooperate.

## What the tool measures

`archcheck` builds the include graph and the dependency graph between areas of a repo, then watches each commit for structural change: an include cycle appearing or growing, a new cross-area edge, a copied block, cognitive complexity climbing, a header turning into a god-header. It reads no meaning. It never calls an LLM. It compares the graph before and after.

The corpus: 1,188 C++ open-source repositories, 484,500 commits, back to mid-2024. AI attribution comes only from commit metadata (bot author, `Co-authored-by`, AI committer), never from the message text, so a human who wrote "fixed per AI suggestion" never lands in the agent bucket.

## Agents were not the problem I expected

I measured seven kinds of drift, matched commits by size, and compared agent code to human code in the same repos:

- **Copy-paste** — agents do slightly less, not more
- **Cognitive complexity** — no difference per commit
- **Include cycles** — humans introduce disproportionately more
- **Boolean flags instead of a state machine** — a human habit, not an agent one
- **God-headers, coupling, chain depth** — no agent-specific signal

The only consistent difference: agent commits run about 1.3x larger. More code, same drift per unit of it.

## What happens when a repo switches to agents

Then I stopped comparing authors and watched what happens to a repository in the weeks around the moment it adopts agents. 361 repos that made the switch, against 265 matched repos that never did.

After adoption, drift and commit volume rise together.

![Drift rises after a repo switches to agents](/assets/images/drift_by_week.png)

In the settled weeks after adoption, cognitive-complexity events accumulate about 2x faster per week, boolean-flag additions about 1.7x, new clones and commits about 1.4x. In the repos that never switched, none of this moves.

Divide by the number of commits or by a thousand lines of code and the climb is gone: there is more code, not worse code per line.

A 2026 CMU study (He, Agarwal, Vasilescu et al., arXiv:2601.13597) reported cognitive complexity rising 39% after teams adopted agents. Their model already controls for lines of code, so this is not a refutation of their number. They measure whether total repository complexity rose. I measure whether each unit of delivered code got more complex. On my corpus, per commit and per thousand changed lines, it did not.

## The line that does not climb is recorded review

![More PRs merge without recorded human review](/assets/images/review_waffle.png)

The share of pull requests merged with no human reviewer recorded rose from 45.8% to 58.1% in the adopting repos. In the never-adopters it stayed flat, 49.2% to 48.0%. The pull requests got bigger too.

This tracks recorded review, not whether a person read the diff. What it shows: generated output grew faster than the human-review process recorded around it. Review capacity does not scale with generation on its own.

## Review bots do not read the graph

Maybe the bots already cover this. I took commits that introduced a new or grown include cycle or a new cross-area dependency, and checked whether they went through a bot-reviewed PR. I started from a known structural regression, so this measures recall on those regressions, not overall review quality.

In 38 such merged PRs reviewed by Copilot, CodeRabbit, Gemini Code Assist, or Sourcery, the bot flagged the structural problem in 2. The other 36 got comments on bugs, style, naming, missing includes, or domain logic while the graph regression merged.

One PR promised to break circular dependencies and created a cycle of seven files. The AI reviewer restated the promise as the result, "breaks circular dependencies... to cut circular includes," and left no comment on any of the 23 changed files. Two humans approved it. It merged.

The bot read the diff and repeated what it claimed. The cycle lives in the graph, one level up from the diff, and nobody built the graph.

[All 38 PRs, with links and the bot's own words.](https://github.com/blurman-ai/archcheck/blob/master/docs/research/bot_review_drift_receipts.md)

## Three cycles the diff did not show

folly: `Future.h` and `Promise.h` include each other through folly's trailing-include idiom. RocksDB: the public `db.h` and an experimental `multi_scan.h` include each other, and the back-edge is a removable forward declaration on a header with huge fan-in. Windows Terminal: `Utils.h` and `SettingContainer.h` include each other, and `SettingContainer` never appears anywhere in `Utils.h` except on that one include line.

None of this is bad engineering. These are mature projects that carry history and sometimes couple on purpose. The point is not to shame an old cycle. It is to catch a new one the moment it lands.

## Limits

Git metadata misses unmarked AI use, so the human bucket is contaminated. Squashed commits distort both attribution and change size. The unit of comparison is the repository, not the individual commit. The study is observational. And archcheck measures physical structure — includes, dependencies, clones, local complexity — not semantic architecture.

## Where it sits next to other tools

![Where archcheck sits next to other C++ tools](/assets/images/tool_comparison.png)

`archcheck` is not a linter, a bug finder, or a formatter, and it does not touch C++ security. It answers one question the others do not: did this pull request make the physical design worse than the baseline. No `compile_commands.json`, because it never compiles: it reads every `#ifdef` branch, not one build. A cycle under `#ifdef _WIN32` is drift even when today's Linux build can't see it. When a path is ambiguous it marks it ambiguous and adds no edge; it does not guess.

## Try it

One static binary, Apache-2.0. Point it at a C++ repo:

    archcheck --diff origin/main..HEAD .

New and grown cycles and new god-headers fail the run. Clones, complexity growth, coupling and flag drift come back as advisories. `--baseline` freezes whatever legacy findings you already have, so day one does not demand a rewrite.

<https://github.com/blurman-ai/archcheck>

The feedback I want is narrow. Which findings are sharp enough that you would let them fail CI. Which should stay advisory. And which structural regressions you currently catch only by memory and luck.
