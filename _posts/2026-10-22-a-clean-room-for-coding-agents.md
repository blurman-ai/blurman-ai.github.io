---
layout: post
title: "A clean room for coding agents"
date: 2026-10-22
permalink: /clean-room/
description: "Fourteen rules for replacing legacy code with a coding agent: behavior cards instead of old code, stored state, one writer, a failure state for every wait."
excerpt: "Phoenix used a clean room to build a compatible BIOS. I use the same separation to keep a coding agent from repeating the code it is supposed to replace."
---

<p class="article-meta">First published 22 October 2026. Last updated 22 October 2026. I will add examples and rules to this article over time.</p>

In 1984 Phoenix Technologies built a BIOS compatible with the IBM PC without copying IBM's code. Engineers who had read the original wrote a specification. A programmer who had never seen IBM's code wrote the new BIOS from it.

I hide old code from my coding agent for another reason: it repeats whatever it sees. When an agent hits a wall in bad code, it patches, like the average author in its training data.

A bug comes in: a user's attempt hangs on step one. The agent fixes it where it hangs. One more condition, one more function that computes the same state its own way. In one day the agent merged four patches into one function. That function derived the attempt's state from the event log across seven tables. The next day the agent wrote that it had never stopped to ask where the attempt keeps its state. The answer was nowhere, and it had been in front of the agent since day one.

This happened right next to a clean room we had built a month earlier. There the agent writes new code from cards that describe the old behavior and never opens the old code. Fourteen rules hold inside the clean room, and each violation can be found with grep or with one question about the diff.

## The fourteen rules

<ol class="rules-summary">
  <li><a href="#rule-1">State is a stored field with a declared list of values and a transition table.</a></li>
  <li><a href="#rule-2">One function writes the state, in one transaction, and rejects any transition missing from the table.</a></li>
  <li><a href="#rule-3">Every wait on an external call has a failure state.</a></li>
  <li><a href="#rule-4">Every transition has a test.</a></li>
  <li><a href="#rule-5">The entity's code lives in one package.</a></li>
  <li><a href="#rule-6">A failure records its reason as a code from a list.</a></li>
  <li><a href="#rule-7">An unknown value, a failed write or an expired lock ends in a failure state.</a></li>
  <li><a href="#rule-8">Code of one kind knows nothing about other kinds.</a></li>
  <li><a href="#rule-9">The new code does not call the old code, and the old code does not call the new.</a></li>
  <li><a href="#rule-10">Parts are accepted separately: a defect in one part does not fail the whole.</a></li>
  <li><a href="#rule-11">Every check has failed at least once on a real defect.</a></li>
  <li><a href="#rule-12">The screen draws the state the server returned.</a></li>
  <li><a href="#rule-13">The outcome does not depend on the order of responses.</a></li>
  <li><a href="#rule-14">Three failed patches: stop and propose an architecture change.</a></li>
</ol>

## How the clean room works

<div class="flow">
  <div class="step"><strong>Old system</strong>code, data, a running instance</div>
  <div class="arrow">→</div>
  <div class="step"><strong>Analyst</strong>reads the old code and runs the old system</div>
  <div class="arrow">→</div>
  <div class="step boundary"><strong>Behavior cards</strong>the only thing that crosses</div>
  <div class="arrow">→</div>
  <div class="step"><strong>Implementer</strong>never opens the old code</div>
  <div class="arrow">→</div>
  <div class="step"><strong>New code</strong>under the fourteen rules</div>
</div>

A card describes one operation from the outside: input, result, failures, and what must stay true. It does not name helpers, tables or the call order of the old code.

<div class="example" markdown="1">

| Part | Description |
|---|---|
| Operation | Start an attempt |
| Input | An authorized user, an assignment, a request identifier |
| Preconditions | Access is valid; the assignment allows another attempt |
| Success | One attempt exists in `queued`; repeating the same request returns that attempt |
| Refusal | A reason code from the catalog says why the attempt cannot start |
| Concurrency | Two deliveries of the same request create one attempt |
| Observation | The caller reads the stored state and, after a failure, its reason code |

A card that says "call this helper, then check that table" carries the old design across the boundary.
</div>

Phoenix's founder Neil J. Colvin describes the process in the foreword to *System BIOS for IBM PC/XT/AT Computers and Compatibles* (Phoenix Technologies, Addison-Wesley, 2nd ed., ISBN 0-201-51806-6, p. xviii). The rules below are mine, not Phoenix's.

## Rules

### <a id="rule-1"></a>1. State is a stored field

<div class="rule" markdown="1">
An entity's state is a stored field with a declared list of values and a transition table, declared once in code. No code derives it from the event log, from whether rows exist, or from a neighbor table. The API returns the stored state; the frontend draws from it. If the frontend needs the list of values, it gets it from the API contract.
</div>

<div class="example" markdown="1">
A reviewer changes an attempt's result from `needs_review` to `passed`. The attempt page and the manager's dashboard both read the stored result. Rebuilding an analytics report cannot bring back `needs_review` from an older event.

<p class="check">Record the reviewer's decision, rebuild the report, and check that both views show <code>passed</code>.</p>
</div>

### <a id="rule-2"></a>2. One function writes the state

<div class="rule" markdown="1">
One function writes the state, in one transaction with the data of the transition, and rejects any transition missing from the table. It also owns the decision: callers pass facts, the function applies the rule. Seven callers that compute seven verdicts and hand them to one setter still have seven owners. Two concurrent callers cannot both move the entity from the same old state.
</div>

<div class="example" markdown="1">
An automatic assessment reports a score and a flag that human review is required. The worker, the HTTP endpoint and the retry handler all send these facts to the attempt's owner. The owner keeps the result in `needs_review` even with a high score until the reviewer decides.

<p class="check">Send the same facts through each entry point; the stored result is identical.</p>
</div>

### <a id="rule-3"></a>3. Every wait has a failure state

<div class="rule" markdown="1">
Every wait on an external call (a model, the network, a queue, a background worker) has a failure state. Failure and timeout are declared transitions. A process outside the waiting worker moves the entity out if that worker dies. No entity is left without a next step.
</div>

<div class="example" markdown="1">
A document parser claims a job with a two-minute lease and crashes. After the lease expires, a watchdog asks the job's owner to move it from `processing` to `failed` with reason `lease_expired`. The document page offers a retry.

<p class="check">Kill the parser after the claim, with no browser tab open. The job reaches <code>failed</code> on its own.</p>
</div>

### <a id="rule-4"></a>4. Every transition has a test

<div class="rule" markdown="1">
Every allowed transition has a test: starting state, event, stored result. Failure transitions too. A forbidden transition has a test that it changes nothing. A contract test sends one payload through both sides of a boundary; a mock does not count as the other side.
</div>

<div class="example" markdown="1">
A provider's deadline expires, and its result arrives late. The test controls the clock: `running → failed` with `provider_timeout`, then the late result is rejected and nothing is published. A second test delivers the result before the deadline and gets `succeeded`.

<p class="check">Each row of the transition table has its test; a transition outside the table is rejected.</p>
</div>

### <a id="rule-5"></a>5. The entity's code lives in one package

<div class="rule" markdown="1">
The state, the transition table and the writer live in one package. Other packages use its public operations. An import contract blocks writes to its state from outside.
</div>

<div class="example" markdown="1">
The `attempts` package exposes `record_answer` and `review_result`. The reporting package reads the public view but cannot import the internal writer or update the attempt through the ORM model.

<p class="check">A fixture where reporting imports the writer fails the import check; use of the public view passes.</p>
</div>

### <a id="rule-6"></a>6. A failure has a reason code

<div class="rule" markdown="1">
A failure records its reason as a code from one catalog. The catalog declares each code's family and whether it can be retried. No decision reads the error message text or the spelling of a code. The same applies to content: a missing section is a declared value, and the label shown to the user is only a label.
</div>

<div class="example" markdown="1">
A provider answers "Too many requests" today and "Rate limit exceeded" tomorrow. The adapter maps the response status to `provider_rate_limited`; the catalog says it is retryable. A document section without text stores `fill: missing`; the renderer prints "Requires clarification".

<p class="check">Two responses with the same status and different messages get the same retry decision. Changing the label does not change which sections count as missing.</p>
</div>

### <a id="rule-7"></a>7. Unknown is not success

<div class="rule" markdown="1">
An unknown value, a failed write or an expired lock ends in a failure state. If the failure itself cannot be stored, the operation reports that it failed, stops dependent work, and recovery finishes the transition later.
</div>

<div class="example" markdown="1">
An assessment has a score, but the database rejects the transaction that saves it. The service reports that the result was not saved and sends no "passed" notification. Recovery repeats the operation by its request identifier.

<p class="check">Inject a commit failure: storage has no successful result, and no success notification leaves the service.</p>
</div>

### <a id="rule-8"></a>8. One kind knows nothing about other kinds

<div class="rule" markdown="1">
Code of one kind knows nothing about other kinds. No "what type am I" checks. The kind is a declared field; nobody guesses it from an identifier prefix, a title, a unit or the presence of a field. A dispatcher picks the handler by that field.
</div>

<div class="example" markdown="1">
An assignment response carries `kind: trainer`. The dispatcher selects the trainer handler, which knows attempts and assessments. The document handler knows versions and acknowledgment. Renaming the trainer or changing its identifier cannot send it to the document handler.

<p class="check">Dispatch the same kind with different titles and identifiers; the handler is always the same.</p>
</div>

### <a id="rule-9"></a>9. New and old code do not call each other

<div class="rule" markdown="1">
The new code does not call the old code, and the old code does not call the new. Every bridge is a named exception in the import contract and goes away with the old path.
</div>

<div class="example" markdown="1">
During migration, one named adapter reads old assignment records and converts them to the new input. The import contract allows only this adapter to read the old schema; its removal condition is "all assignments migrated".

<p class="check">A direct import of the old engine from the new attempt handler fails the dependency check.</p>
</div>

### <a id="rule-10"></a>10. Parts are accepted separately

<div class="rule" markdown="1">
A defect in one part does not fail the whole if the other parts can be accepted. Whether a part is required comes from its type and the plan, not from the place where a check failed. A rejected part keeps its reason code.
</div>

<div class="example" markdown="1">
A course is assembled from four modules. The model returns no text for the quiz module. The three other modules are accepted; the quiz is `failed` with `empty_model_response`, and the course shows which part needs another run. If the plan marks the quiz as required, the whole course is `failed` with the same reason.

<p class="check">Plant an empty response for one optional part: the other parts are published, and the rejected part has its reason code.</p>
</div>

### <a id="rule-11"></a>11. Every check has failed once

<div class="rule" markdown="1">
Every new test and scenario fails at least once on a real defect: revert the fix or plant the defect, and the check must go red. A check measures the visible result, not a sign that code ran: the answer to the question, not status 200; the border color in focus, not an internal variable of a library. A scenario that passes because of the environment (a stale index, data from a previous run, a cache) proves nothing, so it also runs on a clean environment.
</div>

<div class="example" markdown="1">
A test for a timeout fix passes. With the fix reverted it still passes, because it only checks that the endpoint returned 200. The test is rewritten to read the stored state: `failed` with `provider_timeout`. Now it fails on the reverted code and passes on the fix.

<p class="check">The pull request shows a red run of the new test on the reverted code and a green run on the fix.</p>
</div>

### <a id="rule-12"></a>12. The screen draws what the server returned

<div class="rule" markdown="1">
The state of an entity stored on the server comes in one field of the response. The browser does not assemble it from flags, timers, effects or its own storage. The browser keeps only its own state: an open panel, an unsent edit.
</div>

<div class="example" markdown="1">
A draft page chose its step from five fields of three responses and a browser timer. Now the draft response carries `stage`, and the page maps each stage to a view through one table. Closing the tab and opening it on another device shows the same step.

<p class="check">Open the page in each stage with empty browser storage: the view matches the stage from the response.</p>
</div>

### <a id="rule-13"></a>13. The outcome does not depend on the order of responses

<div class="rule" markdown="1">
If a response writes to fields that the user can also change, those fields are locked until the response arrives, or a precedence rule is declared. The speed of an external system does not change the result.
</div>

<div class="example" markdown="1">
The user edits a draft's title while the model is still generating the draft. The generated title arrives after the edit. The declared rule: the user's edit wins, and generated values fill only fields the user has not touched.

<p class="check">Deliver the model response before and after the user's edit: the final title is the user's in both cases.</p>
</div>

### <a id="rule-14"></a>14. Three failed patches mean a design change

<div class="rule" markdown="1">
If three patch attempts did not fix a defect, the agent stops and proposes an architecture change instead of a fourth patch. The proposal names what is missing: a state, a transition, an owner of a decision, a way out of a wait.
</div>

<div class="example" markdown="1">
An upload keeps showing "Processing". Three patches add a browser timeout, another poll and a retry on page reload; the defect returns after a worker restart. Before a fourth patch, the agent proposes a stored processing job with a lease and an expiry transition owned by a watchdog.

<p class="check">Kill the worker, keep the browser closed, open it later: the page shows the recovered state.</p>
</div>

## A small state machine

<div class="example" markdown="1">
A background operation has four stored states. Creating it sets `queued`. There are no automatic retries.

| From | Event | To | Reason |
|---|---|---|---|
| `queued` | Worker claims the operation | `running` | — |
| `queued` | Queue deadline expires | `failed` | `queue_timeout` |
| `running` | Result is committed | `succeeded` | — |
| `running` | Provider refuses the request | `failed` | `provider_rejected` |
| `running` | Call deadline expires | `failed` | `provider_timeout` |
| `running` | Worker lease expires | `failed` | `lease_expired` |

The API returns the stored state and reason. The frontend maps them to a view:

| State | View |
|---|---|
| `queued` | Waiting to start |
| `running` | In progress |
| `succeeded` | Result |
| `failed` | Failure, with an explanation chosen by reason code |

A network error in the browser means the browser could not read the operation, not that the operation failed.
</div>

## How to find a violation

| Rule | Check |
|---|---|
| 1. Stored state | grep for status lists written by hand outside the declaration and the generated API types |
| 2. One writer | grep for assignments to the state field outside its package |
| 3. Failure state | every `queued`, `pending`, `running` has a deadline and a named process that ends it |
| 4. Tests | a test per row of the transition table, plus one forbidden transition |
| 5, 9. Boundaries | an import contract with a forbidden import for each boundary; the list of bridges only shrinks |
| 6. Reason codes | grep for `in str(exc)`, `.includes(message)`, `startswith` on codes |
| 8. Kinds | grep for `startswith` on identifiers and comparisons with titles |
| 10. Parts | a planted defect in one optional part; the other parts are still accepted |
| 11. Failed once | revert the fix; the new test must fail |
| 12. Screen | grep the frontend for server statuses in `useState`, `setTimeout` around a status, entity state in `localStorage` |
| 13. Order | deliver the response before and after the user's action; the results match |

Every check has a case on which it must fail: a planted import, a planted status list, a planted string comparison. One question goes to every diff: **does this change add a second way to compute a fact the system already stores?**

The agent has one path left: a new value in the state list, a row in the transition table, a test for the transition.

This is one way to build the environment I described in [Agent Comfort]({% post_url 2026-10-11-your-agent-is-not-dumb-it-is-uncomfortable %}).

## Article history

- **22 October 2026:** first version, from my LinkedIn post: the Phoenix history, behavior cards, fourteen rules with an example and a check for each, a state machine.
