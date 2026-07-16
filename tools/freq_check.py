"""Flag rare general-vocabulary words in a post body (see backlog/#001).

Usage: python3 tools/freq_check.py article_body.txt
Input: post text with no front matter, no code blocks, no URLs.
Gate:  nothing with zipf < 3.5 that is not a domain term.
"""

import re, sys
from collections import Counter
from wordfreq import zipf_frequency

SKIP = {
    'archcheck', 'folly', 'rocksdb', 'copilot', 'coderabbit', 'gemini', 'sourcery',
    'cmu', 'agarwal', 'vasilescu', 'hil', 'llm', 'pr', 'prs', 'ci', 'win32',
    'ifdef', 'json', 'apache', 'utils', 'settingcontainer', 'multi_scan', 'db',
    'h', 'cpp', 'x', 'et', 'al',
    # added in #001 — proper nouns the reader is not expected to "know" as words:
    'blurman-ai', 'archcheck-demo',  # repository names in links
    'arxiv',                         # the preprint host, part of a citation
}
DOMAIN = {
    'repo', 'repos', 'repository', 'repositories', 'commit', 'commits', 'committer',
    'diff', 'merged', 'linter', 'formatter', 'boolean', 'boolean-flag', 'git',
    'metadata', 'coupling', 'baseline', 'corpus', 'drift', 'clones', 'header',
    'god-header', 'god-headers', 'copy-paste', 'bots', 'bot',
    'bot-reviewed', 'co-authored-by', 'cognitive-complexity', 'cross-module',
    'never-adopters', 'compile', 'compiles', 'dependency', 'dependencies',
    'advisories', 'advisory', 'attribution', 'look-alikes', 'trailing-include',
    # added in #001 — rare in the general corpus, standard for this audience:
    'codebases',    # what the post is about; no plain equivalent that keeps the scale
    'regressions',  # software regression, not statistics; the post's unit of measurement
    'namespace',    # C++ keyword, quoted from the folly mechanism
    'squashed',     # git squash; naming the git operation is the point of the caveat
    'finder',       # "bug finder" — the tool category, as on the comparison chart
    'freezes',      # what --baseline does to existing findings; product vocabulary
    'flagged',      # what a review tool does to a problem; used throughout
    'semantic',     # semantic vs physical architecture — the distinction being drawn
    'reviewer',     # code review vocabulary
    'rewrite',      # "does not demand a rewrite" — software vocabulary
}
text = open(sys.argv[1]).read().lower()
words = re.findall(r"[a-z]+(?:-[a-z]+)*", text)
counts = Counter(w for w in words if w not in SKIP and w not in DOMAIN and len(w) > 2)
rows = sorted((zipf_frequency(w, 'en'), w, n) for w, n in counts.items())
for z, w, n in rows:
    if z < 3.5:
        print(f"{z:5.2f}  {n:3}  {w}")
