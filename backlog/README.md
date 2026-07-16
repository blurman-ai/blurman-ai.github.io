# backlog/

Task directory for this blog. One file = one task.

The posts here are outward-facing and mostly already published, so an edit to a live post is
not a free action: someone may have read the old wording, and every claim in a post is backed
by data in another repository. This backlog exists to answer, months later, **why** a published
sentence changed and **what** it was checked against.

## Structure

```
backlog/
  new/*.md         — created, not started
  wip/*.md         — in progress (has a Started date)
  completed/*.md   — finished; the record of what changed and why
  dropped/*.md     — won't do; exact reason in the "Outcome" section
```

## File-name format

```
NNN_<priority>_<short_name>.md
```

- **NNN** — 3-digit sequential ID, never changes. The `#NNN` reference lives forever.
- **priority** — `blk` (blocker) / `crt` (critical) / `maj` (major) / `min` (minor).
- **short_name** — snake_case.

Example: `001_maj_plain_english_pass.md`.

## Rules specific to a published blog

- **Every factual claim traces to a source.** Posts about `archcheck` cite runs that live in
  `blurman-ai/archcheck` (`docs/research/`, `docs/findings/`, `experiments/`). A task that
  touches a number must name the file, and ideally the command, the number came from. If a
  claim cannot be traced, it does not get edited into the post — it gets recorded as SKIPPED.
- **No silent rewrites of a live post.** Point edits, listed in the task, one line per change.
  Regenerating a published article loses the author's voice and hides what actually moved.
- **The task keeps the verdict, not just the intent.** On completion, record what was APPLIED,
  what was MODIFIED (and why the wording deviated), and what was SKIPPED (and why). That record
  is the point of this directory.
- **The author's phrasing wins.** Deliberate turns of phrase are not defects. When in doubt,
  ask rather than smooth them out.

## Lifecycle

1. Create in `new/`, with a `**Created:**` date.
2. Move to `wip/`, add `**Started:**`, when work begins.
3. On completion, move to `completed/` and fill in the outcome sections.
4. Commits reference the task via `(#NNN)`.
