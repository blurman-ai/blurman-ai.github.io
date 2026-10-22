---
layout: post
title: "A clean room for coding agents"
date: 2026-10-22
permalink: /clean-room/
description: "Behavior cards, explicit state, and ten rules for replacing legacy code without teaching a coding agent to repeat its design."
excerpt: "Phoenix used a clean room to build a compatible BIOS. I use the same separation to keep a coding agent from repeating the architecture it is supposed to replace."
---

*First published 22 October 2026. Last updated 22 October 2026. This article will grow as I add examples and develop the principles.*

In 1984, Phoenix built an IBM PC-compatible BIOS using a clean room. Engineers who studied the original described its behavior. Engineers who had never seen it wrote a new implementation from that description.

I hide old code from my coding agent for another reason: it repeats whatever it sees.

A bug comes in: a user's attempt hangs on step one. The agent fixes it where it hangs. One more condition, one more function that computes the same state its own way. In one day, the agent merged four patches into one function. That function derived the attempt's state from the event log across seven tables. The next day, the agent wrote that it had never stopped to ask where the attempt kept its state.

The answer was nowhere. It had been in front of the agent since day one.

This happened right next to a clean room we had built a month earlier. There, the agent wrote new code from cards describing the old behavior and never opened the old implementation.

For coding agents, I use a **clean room** with an explicit architectural contract. The new implementation has its own state, public interfaces, and rules that can be checked. The clean-room process controls what the implementer can see. The architectural rules define what the resulting code is allowed to do.

## The history: Phoenix and the specification boundary

Phoenix's founder, Neil J. Colvin, describes the process in the foreword to *System BIOS for IBM PC/XT/AT Computers and Compatibles*. He dates the company's PC ROM BIOS breakthrough to May 1984. One group studied the BIOS's functionality and passed descriptions to engineers who had never seen it. That second group wrote the implementation. The purpose was compatibility without copying IBM's code. [Phoenix's own account, p. xviii](https://dokumen.pub/system-bios-for-ibm-pc-xt-at-computers-and-compatibles-the-complete-guide-to-rom-based-system-software-2nbsped-9780201518061-0201518066.html).

The useful idea is the boundary between discovering behavior and implementing it. The specification crosses that boundary. The old implementation stays behind.

In my work, that separation has an architectural purpose. I want to preserve the behavior users need while giving the agent room to choose a different structure. When the old code sits in the context, its helpers, exceptions, and workarounds become the examples from which the agent continues.

The ten rules below are the rules I use for that replacement. They are not rules from Phoenix.

## What crosses the boundary

The analyst can read the old code, inspect data, and run the old system. The implementer gets behavior cards. A card describes an operation from the outside: its input, result, failures, and the conditions that must remain true.

Here is an illustrative card for starting an attempt. It is a small teaching example, not a production specification.

| Part | Description |
|---|---|
| Operation | Start an attempt |
| Input | An authorized user, an assignment, and a request identifier |
| Preconditions | Access is valid and the assignment allows another attempt |
| Success | One attempt exists in `queued`; repeating the same request returns that attempt |
| Refusal | A declared reason code explains why the attempt cannot start |
| Concurrency | Two deliveries of the same request cannot create two attempts |
| Observation | The caller can read the stored state and, after failure, its reason code |

The real card also needs concrete examples, the source of each behavior, and decisions about ambiguous cases. An accidental legacy behavior must be identified before someone turns it into a requirement. If the evidence is missing, the card has a gap to resolve.

“Call this helper, then check that table” carries the old design across the boundary. A card should give the implementer enough information to reproduce the required behavior without that instruction.

## Ten rules inside the clean room

The examples under these rules are illustrative. They show how to apply the principles; they are not reports about the current implementation of a product.

### 1. State is a stored field with declared values and transitions

An entity has a state. Its possible values are declared once, along with a transition table. Readers take that state from its authoritative field.

They do not reconstruct it from an event log, the existence of a neighboring row, a nonempty error field, or several booleans. If the API and frontend need the same values, their types come from the contract. A second handwritten list is a second place for the truth to change.

Events remain useful for history, timing, and diagnosis. In this design, they do not decide the entity's current operational state. Event sourcing makes a different choice of authority; storing the current state is a deliberate choice for this implementation.

**Example.** A reviewer changes an attempt's result from `needs_review` to `passed`. The attempt page and the manager's dashboard both read that stored result. Rebuilding an analytics report cannot turn it back into `needs_review` because an older event says so. A useful test records the reviewer's decision, rebuilds the report, and checks that both views still show `passed`.

### 2. One function owns the transition and the decision behind it

One function writes the state, in one transaction. It checks the current state, rejects a transition missing from the table, and writes the associated result or reason together with the new state.

There is a trap here: seven callers can compute seven different verdicts and pass them to one setter. The assignment has one owner, but the decision still has seven. The rule includes ownership of the decision. Callers provide facts; the owner applies the declared rule.

Concurrent callers must not both advance from the same old state. The transaction needs a mechanism such as a row lock or a conditional update that detects a competing write.

**Example.** An automatic assessment supplies a score and a flag saying human review is required. The attempt owner applies the policy: even a high score leaves the result in `needs_review` until the reviewer decides. The worker, HTTP endpoint, and retry handler all submit assessment facts to that owner. Send the same facts through each entry point and check that the stored result is identical.

### 3. Every wait has a declared way to end

An external call can fail, time out, or outlive the worker making it. Each case needs a declared transition and a process responsible for taking it.

A timeout in the HTTP client covers one wait. A worker killed after storing `running` needs recovery outside that worker: for example, an expiring lease and a watchdog. The watchdog calls the same state owner. A stale worker cannot later overwrite the recovered result.

The same question applies to `queued`, `pending`, and `processing`: who moves the entity out if the process that was supposed to do the work disappears?

**Example.** A document parser claims a job with a two-minute lease and then crashes. After the lease expires, a watchdog asks the job owner to move `processing` to `failed` with reason `lease_expired`. The document page can now offer a retry. Test this by killing the parser after the claim; the recovery must happen even when no browser tab is open.

### 4. Every transition has a test

For each declared edge, a test checks the starting state, the event or command, and the stored result. Failure transitions get tests too.

Rejection needs a control case: attempt a forbidden transition and verify that it changes nothing. Test the boundaries that matter to the operation, including duplicate delivery, timeout, and a late result after lease expiry.

A contract test uses one payload on both sides of a boundary. A mock that repeats what the producer is expected to send cannot establish that the real consumer understands it.

**Example.** A provider starts computing a result, its deadline expires, and the result arrives late. A test controls the clock, takes `running → failed` with `provider_timeout`, and then delivers the result. It checks that the late completion is rejected, the state remains `failed`, and no successful result is published. A separate test delivers the result before the deadline and checks `succeeded`.

### 5. The entity's code lives in one package

The state declaration, transition rules, and owner have a clear home. Other packages use its public operations. An import contract blocks access to internal state writers.

That boundary is part of the design. A comment saying “do not write this field directly” leaves the next agent free to find a convenient assignment elsewhere. An executable dependency rule makes that route visible as a failure.

**Example.** The `attempts` package exposes `record_answer` and `review_result`. A reporting package may read its public view, but it cannot import the internal state writer or update the attempt through an ORM model. Give the dependency check a fixture where reporting imports that writer: it must reject the import. Ordinary use of the public read interface must pass.

### 6. Reason codes carry meaning; message text does not

A failure records its reason as a code from one catalog. If callers need a failure family or a `retryable` property, the catalog declares them. Callers do not recover those properties from a code's spelling.

No decision reads the error message text. Messages can change with translation or better wording. The code carries the meaning.

This applies beyond errors. A missing document section needs a declared value such as `fill: missing`. The renderer can print “Requires clarification.” Changing that label must not change whether the section counts as missing.

**Example.** A provider returns “Too many requests” today and “Rate limit exceeded” tomorrow. The provider adapter maps the structured response status to `provider_rate_limited`. Its catalog entry declares the family and retry policy. The retry handler reads those declared properties. Test two responses with the same status and different messages: the retry decision must stay the same.

### 7. Unknown values and failed writes stop progress

An unknown state cannot quietly mean success. A failed write cannot be reported as a completed transition. An expired lease cannot leave its former owner free to keep changing the entity.

“End in a failure state” needs a precise implementation. If the database is unavailable, the process cannot promise that it has stored `failed`. It must report the failed operation, stop dependent work, and leave a recovery mechanism able to finish the transition when storage returns.

The property is that uncertainty never grants permission to continue as if the operation succeeded.

**Example.** An assessment has produced a score, but the database rejects the transaction that would save it. The service reports that the result could not be saved and does not send a “passed” notification. Recovery retries the operation using its request identifier. Inject a commit failure and check both boundaries: no successful result in storage, and no success notification sent outside the service.

### 8. Code for one kind knows nothing about other kinds

A course handler does not keep asking whether it is actually handling a trainer. A trainer handler does not contain branches for documents. Dispatch happens at a declared boundary, using an explicit kind from the contract. Inside that boundary, each implementation works with its own kind.

The caller does not guess the kind from an identifier prefix, a unit of volume, a title, or the presence of a field. Adding another kind should not require editing a growing chain of guesses throughout the system.

**Example.** An assignment response declares `kind: trainer`. A dispatcher selects the trainer handler, which knows about attempts and assessments. A document handler knows about versions and acknowledgment. Renaming the trainer or changing its identifier cannot select the document handler. Test dispatch with the same declared kind and several titles and identifiers; selection must depend only on the kind.

### 9. The new and old implementations are isolated

The new implementation does not call the old implementation, and the old implementation does not call into its internals. Every necessary migration bridge is a named exception in the import contract, with a removal condition tied to the old path.

This gives migration a visible boundary. An exception can be reviewed and removed. An ordinary import of a convenient legacy helper can quietly bring the old design back into the room.

**Example.** During migration, a named adapter reads an old assignment record and converts it to the new input contract. The import contract permits that adapter alone to read the legacy schema. It does not permit the new attempt handler to invoke the old attempt engine. The exception names its removal condition: all assignments have been migrated. A direct import of the old engine must fail the dependency check.

### 10. Three failed patches trigger an architecture proposal

If three patch attempts have not fixed a defect, the agent stops and proposes an architecture change before trying a fourth patch.

The proposal has to name the missing concept or broken ownership: a state that does not exist, an undeclared transition, a decision made by several readers, a wait without an owner. “Refactor this function” is not enough.

Three is the stopping rule I use. It is not a measured universal optimum. Its purpose is to force the question that the agent in the opening story never asked.

**Example.** An upload keeps showing “Processing.” Three patches add a browser timeout, another poll, and a retry on page reload. The defect returns after a worker restart. Before patch four, the agent proposes a durable processing job, a lease, and a declared expiry transition owned by a watchdog. Acceptance becomes concrete: kill the worker, keep the browser closed, then reopen it and read the recovered state.

## A small state machine

Consider a background operation with four stored states: `queued`, `running`, `succeeded`, and `failed`. Creating it establishes `queued`. The following table is an illustrative design with no automatic retries.

| From | Event | To | Reason |
|---|---|---|---|
| `queued` | Worker claims the operation | `running` | — |
| `queued` | Queue deadline expires | `failed` | `queue_timeout` |
| `running` | Result is committed | `succeeded` | — |
| `running` | Provider refuses the request | `failed` | `provider_rejected` |
| `running` | Call deadline expires | `failed` | `provider_timeout` |
| `running` | Worker lease expires | `failed` | `lease_expired` |

The reason codes are declared values. Each row has a test. A transition absent from the table is rejected. A late provider response after `lease_expired` cannot turn `failed` into `succeeded`.

The result and `succeeded` are committed together. If a provider also performs an external side effect, this database transaction alone cannot make the whole operation atomic. The behavior card must specify duplicate handling and recovery at that boundary too.

The API returns the stored state and reason. The frontend maps them to a view:

| State | View |
|---|---|
| `queued` | Waiting to start |
| `running` | In progress |
| `succeeded` | Result |
| `failed` | Failure, with an explanation selected by reason code |

The browser can have its own local state for an open panel or an unsent edit. It does not need a second account of the server operation's lifecycle. A network error means the browser could not read the operation; it does not establish that the operation failed.

## Making the principles checkable

Some rules fit a search. Others need syntax analysis, dependency checks, or a question about the diff.

| Principle | A useful check |
|---|---|
| One declaration | Find handwritten copies of a state list outside the contract or generated code |
| One owner | Find state assignments outside the owning module; review where transition decisions are made |
| Bounded waiting | Require a deadline and a named recovery owner for each waiting state |
| Structured meaning | Find decisions based on message text, display labels, or identifier prefixes |
| Isolated paths | Enforce forbidden imports and an explicit list of migration exceptions |
| Tested transitions | Exercise allowed edges and rejected edges, including races with recovery |

A check must fail on a known violating example. Otherwise a green result says little about whether the rule is being enforced. A broad grep is a search aid; it is not automatically an architecture gate.

I also ask one question about each diff: **did this change add a new interpretation of a fact the system already owns?** A second status resolver, a second verdict function, or a second list of failure values deserves an answer before it becomes context for the next agent.

This is one way to build the environment I described in [Agent Comfort]({% post_url 2026-10-11-your-agent-is-not-dumb-it-is-uncomfortable %}). The cards give the agent behavior to implement. The architectural contract gives it a structure in which to work. The checks make departures visible.

When the next requirement arrives, the route is explicit: change the declared model, add the transition if one is needed, and test the behavior. The architecture question comes before the fourth patch.

## Article history

- **22 October 2026:** Initial version, expanded from my LinkedIn post: the Phoenix history, behavior cards, ten principles with an example and a check for each, and an illustrative state machine.
