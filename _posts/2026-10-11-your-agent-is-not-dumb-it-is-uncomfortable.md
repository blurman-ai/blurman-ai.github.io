---
layout: post
title: "Your agent isn't dumb. It's uncomfortable."
date: 2026-10-11
---

*A shorter English version of [my article on Habr](https://habr.com/ru/articles/1064012/) (in Russian, July 2026), with measurements I have made since.*

Two stories keep repeating in talk about agent development. Engineers are drowning in review of generated code: the [LinearB 2026 benchmark](https://linearb.io/dev-interrupted/podcast/linearb-2026-benchmarks-ai-pr-merge-rate) covers 8.1 million pull requests and reports about twice as many merges with AI, review time up 91%, and AI-written PRs waiting 4.6 times longer for a reviewer. Product managers, meanwhile, say they ship features without programmers. The [Meta product manager](https://www.aol.com/news/meta-product-manager-no-technical-060448066.html) whose vibe-coding "superpower" went around the feeds hands his code to a developer for final review. It is a Formula 1 car with men shovelling coal under the hood.

This article proposes Agent Comfort: a property of the development environment that you can measure and raise on purpose, so that the environment does the work of the men under the hood.

## What Agent Comfort is

Agent Comfort is how easy the environment makes it for an agent to find its way in the context, use the tools it has, and check its own work. The metric is First-Prompt Success Rate:

```
FPSR = tasks closed from the first prompt / all tasks
```

If the agent closed 8 tasks out of 10 from the first prompt, FPSR is 0.8. "First prompt" means the prompt that starts the session. The number of iterations the agent ran inside does not count. What counts is that a human did not come back to the chat to clarify the task or answer the agent's questions.

Comfort rests on three parts of the environment.

**Clean context.** A clear structure, the change history at hand, no dead legacy in the way. Every extra file in the context costs tokens and adds one more chance to read the system wrong.

**Tools that just run.** The agent should not have to guess how to build the project, how to run the tests, or where the logs are. One command starts everything, the output can be read as is, and the result repeats.

**Sensors in the verification loop.** Ways to look at the work while it is still in progress. In a geometry task: build a profile of the 3D surface and read its properties at a point. In a web service: the number of database queries per operation, where the request time goes, load figures from monitoring. A sensor is an oscilloscope. It gives no pass/fail verdict. It shows numbers and words that the agent can steer by. The requirements have to be consistent and possible to meet, or the sensors will show progress toward a goal that does not exist.

![Sensors along the road show the agent where it is](/assets/images/agent_comfort_sensors.jpg)

High comfort partly replaces model intelligence. When the knowledge already sits in the context and in the verification loop, Sonnet closes tickets on its own, with no plan written by a stronger model first.

The human stays out of the inner cycle of change, check, fix. The human sets up the environment, states the goal, and judges the result.

## The matrix: Agent Comfort × Human Comfort

Human Comfort is the paired idea: how much engineering expertise a person has to add to their intent before the agent can do the task. The less expertise, the higher the comfort. At the top is a requirement in product language: "when the link is lost, the boat must stop safely and tell the operator why". The agent will then ask itself where the timeout value should live. In an uncomfortable environment that question goes to the human, and both Human Comfort and FPSR drop. In a comfortable one the answer is already in the project conventions, the decision history, or the config.

| Agent Comfort | Human Comfort | Mode |
|---|---|---|
| Low | Low | Swamp of Despair |
| Low | High | Cheap Lottery |
| High | Low | Heroic Prompting |
| High | High | Paved Road |

**Swamp of Despair.** Legacy code, weak context, poor tools. The engineer has to know the system in detail, explain it to the agent, and still pull the agent out again and again. You pay in tokens and in engineering time.

**Cheap Lottery.** The human states a wish and gets a result, sometimes the expected one. The agent works where it cannot find its way or check itself, and when it comes back with questions, a person without engineering expertise cannot answer them. Most vibe coding lives here. The risk is postponed until production, or until an engineer cleans it up in code review.

**Heroic Prompting.** The agent can do a hard task, but the engineer loads the missing knowledge into it by hand every time: architecture, constraints, invariants, ways to check, the odd parts of the legacy code. The result is usually the expected one, and the engineer pays for it again on every task.

**Paved Road.** The knowledge is already in the environment. The human states product intent, and the agent collects the engineering context from the repository, the specs, and the decision history. The road is built once and serves every next task.

![The four modes of the Agent Comfort and Human Comfort matrix](/assets/images/agent_comfort_matrix.jpg)

## Gates

Gates are a separate layer from comfort, and agent development does not work without them. A gate is a deterministic pass/fail check of an invariant: unit, contract and regression tests, linters, static analyzers, metrics with thresholds, architecture checkers. For C++ I wrote one myself, [archcheck]({% post_url 2026-07-15-i-built-archcheck-to-prove-agents-wreck-cpp-architecture %}).

Gates protect the architecture, the infrastructure and the users. They also protect the environment from the agent. An agent leaves behind duplicates, outdated comments, a second version of the truth, and all of it becomes the context of the next task. Low comfort produces code that lowers comfort further. Gates break that loop.

What happens without them is on record. The Replit agent [deleted the production database](https://fortune.com/2025/07/23/ai-coding-tool-replit-wiped-database-called-it-a-catastrophic-failure/) of the SaaStr founder, because the test and production databases were not separated. Tea App [exposed 72,000 user images](https://www.nbcnews.com/tech/social-media/tea-app-hacked-13000-photos-leaked-4chan-call-action-rcna221139), government IDs among them: the storage was left on default settings and nobody had to break in. A [review of seven such incidents in six months](https://getautonoma.com/blog/vibe-coding-failures) finds the same thing in each: no verification layer between the agent's output and production.

The Meta product manager solves this the old way, with a gate made of a living engineer. It works and it does not scale: the more code agents generate, the more review lands on people. Automatic gates take the part of that work that can be written as an invariant and checked by a machine. On the Paved Road the engineer builds the environment, comfort and gates, and the agent works with the product manager directly.

## Agent Comfort in loop engineering

The industry has tried three times to cover an uncomfortable environment with a layer on top. First a human wrote a detailed plan and the agent followed it. Then the plan went to a strong model: it loads all the knowledge about the system into a plan, and a cheaper model walks through it. Both are dead ends. The knowledge is spent again on every task, and the environment stays as unclear to the agent as it was.

The third wave is loop engineering: design the cycle and leave the prompting to it. In May 2026 Claude Code got the [`/goal`](https://code.claude.com/docs/en/goal) command. You state a completion condition, the agent runs iterations on its own, and after each turn a small model reads the conversation and decides whether the goal is reached. It works: Boris Cherny, who created Claude Code, [landed 259 PRs in 30 days](https://x.com/bcherny/status/2004887829252317325), all written by Claude Code.

The checking model in `/goal` is not a deterministic check. It runs no commands and reads no files. It judges by the text of the conversation. Technically `/goal` is a Stop hook that asks a model after each turn, and the same hook can run a script, so that code gives the verdict. The [Proof-or-Stop](https://arxiv.org/abs/2607.14890) paper (July 2026) asks for exactly that: an agent's result is only a claim until a check confirms it, one that can be run and repeated without the model.

The cost of a loop is set by how fast it converges, and convergence is set by the environment. There are five easy ways to break a loop:

- **A goal that cannot be checked.** The author of [one write-up](https://vc.ru/ai/2982760-problemy-s-claude-code-i-rezhim-goal) left "make the settings screen more convenient" to run overnight. In the morning: 217 turns, zero commits, two thirds of the weekly limit gone. The agent moved the layout back and forth all night.
- **A context that overflows.** In [another public write-up](https://dev.to/ailnk0/claude-code-stuck-in-a-failure-loop-i-escaped-with-multi-agent-16di) Claude Code ran the loop "approach A, wall, approach B, back to A". The task did not fit in the context, and every automatic compaction blurred the early decisions.
- **Sensors that have come loose from the product.** In a chart-processing project of mine, the review viewer drew its picture through an old duplicate code path. That path disagreed with the production classifier on 8 to 10% of faces on every chart. I spent turns steering the agent to remove noise that the production output did not contain.

The other two are requirements that contradict each other and a loop with no limit on iterations.

`/goal` in an uncomfortable environment is a shot at goal in the dark. It pays off only if you are spending tokens on purpose. Some companies did put token use into developer KPIs, and [have since backed off](https://fortune.com/2026/05/28/tokenmaxxing-is-dead-companies-didnt-get-the-roi-from-ai-they-wanted-to-see/): Meta and Amazon removed their internal token leaderboards, and Duolingo withdrew its plan to rate employees by AI use.

## Three measurements

**A physics model written by the agent.** In Rumba, a math model of a tracked vehicle, the agent wrote 12,788 lines of code. A scenario player served as both sensor and gate. It ran tests that Claude generated in batches from the specs and from expert remarks, and it returned a trace of intermediate states and a verdict on them. My work was the environment: I chose the metrics and the closed-loop checks, found documentation, filled the gaps in the context, and removed contradictions when the agent got confused. The story of the project is in ["Claude in the gears"](https://habr.com/ru/articles/1045911/) (in Russian).

**Task lifetime in a product team.** Backend and frontend had separate owners. A change that touched both took two hours of coding and two days on the calendar, because the second owner picked up the ticket the next day. At the end of July I changed the environment:

- all repositories under one workspace;
- task context moved into Git;
- machine-readable contracts pinned;
- local checks made the same as the checks in CI;
- machine gates on risky production actions;
- read access for agents to production logs and Grafana dashboards.

| | Before (113 tasks) | After (222 tasks) |
|---|---|---|
| Median lifetime of a completed task | 14 days | about 1.4 days |
| Closed within a day | 4% | about 45% |

This is cycle time. I did not count FPSR in that project. What changed is that one engineer with an agent can take a feature through backend, frontend and infrastructure without waiting for a second specialist.

**One page against 28.** An LLM-maintained wiki makes sense when the sources are a mixed and contradictory set of documents. On a small codebase the idea turns over. In archcheck I built a 28-page wiki from the sources and asked agents the same questions with and without it. Tokens below are marginal: an agent that does nothing already costs 24.3k tokens of system prompt, tools and project context.

Four lookup questions, all answered correctly in every arm:

| Arm | Tool calls | Tokens | Wall-clock |
|---|---|---|---|
| grep the code | 10 | 27.3k | 93.7 s |
| 28-page wiki, verify against code | 10 | 27.6k | 92.3 s |
| 28-page wiki, trust it | 10 | 29.8k | 60.2 s |
| one-page map, trust it | 4 | 13.8k | 31.4 s |

A harder five-part question before a code change, both arms fully correct:

| Arm | Tool calls | Tokens | Wall-clock |
|---|---|---|---|
| grep the code | 12 | 16.5k | 52.9 s |
| one-page map, trust it | 1 | 7.2k | 13.3 s |

The 28 pages cost 9% more tokens than grep. Where one rule is one file of about 100 lines, the wiki pages were larger than the files they described: reading the rule-set source cost 2.7k tokens, and reading the wiki entry map plus its source-map page cost 7.5k. The wiki also went stale at once. A staleness check flagged 8 pages the same day, after unrelated commits. I deleted 27 pages and kept one dense map of facts that no single file in the repository holds. It cut tokens by 49% on lookups and by 56% on the harder question, and tool calls by 92%.

It works under three conditions. The file is shorter than what it replaces. The agent reaches it at once, with no links in between. The instructions name the file as the source of truth, or the agent will read it and go into the code anyway. Next to it there has to be an automatic check that the file is not out of date. An [ETH Zurich study](https://arxiv.org/abs/2602.11988) of repository context files points the same way: generated files lowered task success by about 3%, and files written by people raised it by about 4%.

## How to raise Agent Comfort

Signs of low Agent Comfort:

- The agent asks questions whose answers are in the repository.
- It reads the same files several times in one session.
- It changes code so that it contradicts the code next to it or the documentation.
- It "fixes" failing tests by changing the expected values to match the actual ones.
- Every session starts with digging: the agent builds again the picture it already built yesterday.
- "Honest caveats" multiply in answers and in code: for now, placeholder, simplified, not verified. The agent quietly gives up responsibility for what it did not check.

The last sign can be counted. In July I ran a regex count over three of my repositories: 9,798 tracked files and 1,323 distinct places with caveat wording. Of those, 744 said "advisory", 330 postponed something ("for now", "later", "not yet"), 167 marked a stand-in ("placeholder", "simplified"), and 32 named a check left open ("not verified", "not measured"). A regex cannot tell a real caveat from a normal product term, so 1,323 is not a count of errors. It is the size of the layer that someone has to read by hand.

Most of these signs come from two causes: contradictions and gaps in the context. A contradiction is two versions of the truth in the repository. Documentation disagrees with the code or with another copy of itself, a comment disagrees with the code under it, CLAUDE.md disagrees with the real project structure. The classic is a comment that survived a code change:

```cpp
// try all 4 directions
for (int dir = 0; dir < 8; dir++)
```

A person filters this out without thinking, because they know how it really is. The agent does not know, and picks the wrong version. A gap is missing knowledge, which the agent silently fills with something that sounds right.

Raising comfort is work in two directions.

The first is context: find and close the contradictions and the gaps. Ask your agent, at its highest reasoning setting, to find every contradiction in its working context and to say how each one affects what it generates. Make it a rule: when the agent gets confused, do not correct its answer. Find every source that confused it and fix or delete the wrong ones. And remember that a constraint placed in the context does not hold for the whole session. The agent follows it while it stays in the window, and the window gets worse as the session goes on.

The second is verification: choose the right angles from which the agent looks at its own work. A good angle turns an intermediate result into a metric the agent can optimize, so it can move toward the goal without waiting for a final verdict.

One thing has changed here. Sensors are as useful as ever, and making them has stopped costing anything. Observability code was always expensive, boring work that moved to the end of the backlog. Now the agent builds an instrument for a chosen angle in minutes. The scarce resource is the choice of angle, and that stays with the human.

## What the vendors recommend

While I was writing the original, Claude Opus 5 came out with an [official prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5). Its advice for agentic coding: the model works best when it gets the full task specification up front and then works alone. That is the Heroic Prompting quadrant. All the engineering knowledge goes into the prompt again.

The guide also says that Opus 5 checks its own work, and asks you to remove "double-check" instructions from prompts, since they overlap with the built-in behavior and cost extra tokens. For the new models Anthropic removed more than 80% of the Claude Code system prompt with no loss in quality. Rules that protected against the weak spots of earlier models had become noise that competed for attention with the real instructions.

Vendor guides lead to Heroic Prompting because it is the best mode you can reach without working on the environment. The Paved Road you have to build yourself.

From the other side came the old school. Robert Martin, the author of "Clean Code", [wrote in July](https://x.com/unclebobmartin/status/2080257779395154409) that his current strategy is to not read the code his agents write. He puts gates around the agents: unit tests, Gherkin scenarios, quality metrics, mutation testing, coverage.

## Conclusion

Engineers are drowning in review because today they are the gates, and living gates do not scale with generation. Higher Agent Comfort and automated invariant checks take that work off people. The agent works in a clean environment and reaches the goal in fewer iterations, the checks keep broken code out of production, and the human looks at the result and chooses the angles for automatic verification.

If you have read this far, try giving this article to your agent at the end of a long, hard chat full of errors and disappointment. The result may surprise you.
