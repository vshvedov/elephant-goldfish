---
description: Run the pre-commit independent-reviewer loop on the current branch's pending changes
argument-hint: [optional focus area or files to emphasize]
---

Run the pre-commit review loop. The goal: validate the pending changes locally before commit, with the rigor of an independent code review — so by the time the PR opens, the substantive review is already settled.

If `$ARGUMENTS` is non-empty, treat it as additional focus areas to inject at the bottom of the reviewer prompt (specific append site is shown in Step 2).

## Step 0: Decide whether to run

**Skip the loop for:** pure documentation-only commits (no code touched), single-line typo fixes, version bumps, dependency updates with no code changes, formatter-only diffs, merge commits.

**Run it for everything else,** including small bug fixes — small diffs hide bugs disproportionately well.

## Step 1: Pre-flight (sequentially, NOT chained with `&&`)

Each of these is independent — do not short-circuit on a single failure.

```sh
[BOOTSTRAP: lint command]
```
- New errors introduced by the diff are blockers; pre-existing errors are out of scope. If unsure whether an error is new, baseline against `main`:
  ```sh
  cd "$(git rev-parse --show-toplevel)"
  STASH_REF=$(git stash create --include-untracked)
  if [ -n "$STASH_REF" ]; then
    git stash store -m "lint-baseline" "$STASH_REF"
    trap 'git stash pop' EXIT INT TERM
    git checkout -- :/ && git clean -fd :/
  fi
  [BOOTSTRAP: lint command] > /tmp/baseline-lint.txt 2>&1
  ```
  Then diff your current output against the baseline. New errors only are blockers. The trap restores your work even on Ctrl+C; if the shell dies entirely, your work is in `git stash list` under "lint-baseline".

[BOOTSTRAP: typecheck block — include if the language has a separate type-check step, otherwise remove this entire block]
```sh
[BOOTSTRAP: typecheck command]
```
- Same baseline-diff approach as lint if the codebase is not currently strict-clean on `main`. Only NEW errors introduced by your diff are blockers.

```sh
[BOOTSTRAP: unit test command]
```
- If a test fails because your implementation legitimately changed its expected behavior, do NOT rewrite the test silently — run the reviewer FIRST (Step 2) with the failing test name in `$ARGUMENTS` as a focus area, then update the test only after the reviewer signs off on the new behavior.
- If a test fails for any other reason, fix the code first.

[BOOTSTRAP: e2e test block — include if the project has E2E tests, otherwise remove. Skip-condition guidance per stack.]
```sh
[BOOTSTRAP: e2e test command]
```
- Skip if your diff is purely [BOOTSTRAP: list of layers that don't need E2E, e.g. "model/worker/lib changes with no UI or API surface touched"].

[BOOTSTRAP: code-generation block — include if a build-runner / codegen step is required, e.g. for Flutter `.g.dart` files, protobuf, GraphQL codegen]
If your diff modifies [BOOTSTRAP: what triggers regeneration], regenerate first:
```sh
[BOOTSTRAP: codegen command]
```
Both source and generated files must be committed together.

## Step 2: Spawn a fresh independent reviewer

Use the `Agent` tool with:
- `subagent_type: "general-purpose"`
- `description: "Independent pre-commit review (round N)"` — substitute the actual round number so per-round invocations are distinguishable in telemetry while sharing the loop-grouping prefix.

The reviewer must have NO implementation context — that asymmetry is what makes the review effective.

**Pass the prompt EXACTLY.** Do NOT prepend the implementation plan, the user's original request, what you were trying to do, or any explanation of intent. Any framing leaks the asymmetry.

**The prompt to send to `Agent`'s `prompt` field is exactly the body delimited by `<<<TEMPLATE_START>>>` (exclusive) and `<<<TEMPLATE_END>>>` (exclusive).** Do NOT include the markers themselves. If `$ARGUMENTS` is non-empty, replace the literal `[NO ADDITIONAL FOCUS]` line with `Additionally focus on: <$ARGUMENTS verbatim>`. Modify NO other line.

```
<<<TEMPLATE_START>>>
Independent code review of the pending changes on this branch.

Run ALL of the following to capture every kind of pending change — any one of them in isolation can be empty:
- `git status` (working-tree state, untracked files)
- `git diff` (uncommitted unstaged changes)
- `git diff --cached` (uncommitted staged changes)
- `git diff main...HEAD` (committed-but-unmerged changes; empty when the branch IS `main`)
- `git log main..HEAD --oneline` (commit messages on the branch)

Also `git ls-files --others --exclude-standard` to find untracked new files. Read the touched files in full where the diff context is not enough.

Find substantive issues. For each finding: cite file:line, name the issue, explain WHY it is a bug or risk (not just what the code does), and suggest a concrete fix. Be specific — vague observations are not actionable.

Hunt for:
- Bugs: off-by-ones, null/undefined dereference, wrong variable used, type coercion gotchas, unhandled promise rejections, missing await, async/await misuse, mutating function args, returning the wrong value on an error path
- Security: command injection, XSS, SQL injection, path traversal, prototype pollution, unsanitized input, secrets in URLs or logs, missing auth checks, missing CSRF, open redirects, IDOR (user accessing another user's data via predictable IDs)
- Race conditions: shared state without locks, async ordering, double-submit, event handler re-entry, TOCTOU
- Edge cases: empty arrays, NaN, Infinity, zero, negative numbers, very large numbers, Unicode, timezone, leap seconds, concurrent access, network failure, partial writes
- Error handling: silent catches, swallowed errors, fallback paths that mask real failures, missing error propagation, throwing in finally/destructors
- Performance: N+1 queries, sync work in hot loops, missing memoization, layout thrashing, unbounded growth, missing pagination
- Test coverage gaps: code paths not covered by unit / integration / E2E. For bug fixes specifically: is there a regression test that fails before the fix and passes after?
[BOOTSTRAP: stack-specific Hunt for items go here as additional bullets, e.g.:
- Rails gotchas: missing `includes`, mass assignment without `params.permit`, raw SQL, missing CanCanCan auth, multi-tenant scoping (queries that don't filter by current_company)
- Solid.js gotchas: signal accessors called outside reactive contexts, missing `<For>` keys, store mutation outside `produce`, missing effect cleanup, stale closures over signals
- Flutter / Dart: streams not closed, controllers not disposed in `dispose()`, BLoC race with dispose, Provider scope mismatches, `setState` after dispose, missing `const` constructors in hot rebuild paths
- Cloudflare Workers: request-scope leaks, D1 transaction semantics, R2 binding misuse, session fixation, exposing internal IDs, COOP/COEP header regressions
- Real-time audio / DSP: allocations in `process()`, lock-free invariants, parameter smoothing correctness, sample-rate assumptions, NaN/Inf safety
- Generated code drift: source modified but generated files (.g.dart, *_pb.go, etc.) not regenerated]
- Project-rule violations from CLAUDE.md (cite the relevant section)
- Dead code, leftover console.log/debugger/print/binding.pry, stale comments referencing removed code

Do NOT surface:
- Stylistic preferences (formatting, naming, ordering)
- Suggestions to add explanatory comments unless the WHY is genuinely non-obvious
- Micro-refactors that do not fix a bug
- Speculative concerns ("this could maybe break if...") without a concrete failure mode

[NO ADDITIONAL FOCUS]

Output format: numbered list. For each finding, lead with `file:line` then the issue and fix. End the response with the literal string `no findings` if (and only if) the diff is clean. If you have findings, do NOT include `no findings`.
<<<TEMPLATE_END>>>
```

## Step 3: Triage the findings

For each finding the reviewer returns:
- **Fix it** — apply the change. Note the file:line that was touched.
- **Rebut it** — write a one-line reason. Valid categories: (a) "not a bug because X" with X visible in the diff or codebase; (b) "out of scope — the diff doesn't touch that area"; (c) "intentional trade-off documented in [file:line or CLAUDE.md section]"; (d) "user explicitly asked for this in this conversation" — quote the user's exact words verbatim. Reject vague intent claims ("I meant to do that") that the reviewer cannot verify — fix the code instead.

**Surface every rebuttal back to the user verbatim** in the final report. NO silent dismissals; NO summarizing rebuttals away.

## Step 4: Maintain a ledger and re-invoke

Before re-invoking, print to the user:
```
Open findings going into round N:
- [from round 1] file:line — fixed (commit not yet made; in-flight)
- [from round 1] file:line — rebutted: <verbatim reason>
[...]
```
This makes the working state visible and prevents earlier-round findings from quietly disappearing.

Then re-invoke. Subagents are stateless — re-include the FULL original template body (every line between the `<<<TEMPLATE_START>>>` / `<<<TEMPLATE_END>>>` markers from Step 2), then a blank line, then `---`, then a blank line, then this addendum:

```
Previous round's fixes:
- file:line — what changed
[...]

Verify each fix is correct and complete. Look for anything you missed in the first pass, especially issues introduced by the fixes themselves.
```

Send the concatenated result as the `prompt` argument to `Agent`. Do NOT send placeholder strings — actually paste the body.

## Step 5: Loop with hard cap

Repeat steps 3-4 until the reviewer returns the literal string `no findings` AND every prior-round finding is fixed-or-rebutted.

**Hard cap: 5 rounds.** Stop if (a) you hit 5 rounds without exiting, or (b) any new finding lands at the same `file:method` (or within ~10 lines of a previously-fixed line).

When tripped, print a plain-language brief of open findings grouped by severity (~30 seconds to read), then call `AskUserQuestion`:
- `question`: "Review hit the 5-round cap with N findings still open. What do you want to do?"
- `header`: `"R5 cap"`
- `multiSelect`: `false`
- `options`:
  1. **Accept and commit** — "Skip the open findings, commit as-is."
  2. **Keep working on fixes** — "I'll keep iterating past the cap. Risk: it may not converge — say stop anytime."
  3. **Abandon the change** — "Roll back and start over with a different approach."

If they pick "Accept and commit", proceed to Step 6. If "Keep working", run round 6 (and surface the same brief + question after each subsequent round). If "Abandon", stop and wait for further direction.

Typical loop length: 2-3 rounds. If you're at 5+ without exit, the implementation needs deeper rework, not more reviews.

## Step 6: Final report

Once the loop exits, print to the user:
- Rounds run
- Findings fixed (with file:line each)
- Findings rebutted (with the **verbatim** one-line reason each, not summarized)
- Whether any pre-existing lint/typecheck/test errors were noted as out-of-scope

**STOP at this step.** Do NOT run `git commit`, do NOT run `git add`, and do NOT prompt "want me to commit?" — even in auto mode. Wait for the user's literal commit instruction. [BOOTSTRAP: commit policy reminder, e.g. "Follow the commit convention visible in `git log` (plain message, optional `Fix #<n>:` reference)." or "No `Co-Authored-By: Claude` trailers." Tailor based on what was observed.]
