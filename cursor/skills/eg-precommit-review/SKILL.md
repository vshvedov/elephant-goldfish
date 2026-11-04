---
name: eg-precommit-review
description: Run the pre-commit independent-reviewer loop on the current branch's pending changes — pre-flight checks, fresh goldfish reviewer, round-by-round triage, hard 5-round cap. Use when the user asks for a review, before committing, or before opening a PR.
disable-model-invocation: true
---

Run the pre-commit review loop. The goal: validate the pending changes locally before commit, with the rigor of an independent code review. The reviewer is itself a goldfish — it sees only the diff, not the conversation.

## Step 0: Decide whether to run

**Skip the loop for:** pure documentation-only commits (no code touched), single-line typo fixes, version bumps, dependency updates with no code changes, formatter-only diffs, merge commits.

**Run it for everything else.**

## Step 1: Pre-flight (sequentially, NOT chained with `&&`)

Execute these using the `Shell` tool. Run each command separately so a failure in one does not skip the others.

[BOOTSTRAP: code-generation block — keep only if the stack requires codegen before tests (build_runner, protoc, prisma generate, etc.).]
```sh
[BOOTSTRAP: codegen command]
```

```sh
[BOOTSTRAP: lint command]
```
- New errors introduced by the diff are blockers. Pre-existing errors on untouched files are out of scope (note them, don't fix them).

[BOOTSTRAP: typecheck block — keep this block if the language has a separate type-check step; remove the heading and command if not.]
```sh
[BOOTSTRAP: typecheck command]
```

```sh
[BOOTSTRAP: unit test command]
```
- If a test fails because your implementation legitimately changed its expected behavior, do NOT rewrite the test silently. Surface the expectation change to the user, then update the test deliberately.

[BOOTSTRAP: e2e test block — keep if the stack has an E2E suite; remove otherwise.]
```sh
[BOOTSTRAP: e2e test command]
```

## Step 2: Spawn a fresh independent reviewer

Use the `Task` tool with:
- `subagent_type: "generalPurpose"`
- `description: "Goldfish precommit review"`

The reviewer must have NO implementation context — that asymmetry is what makes the review effective.

**Pass the prompt EXACTLY.** Do NOT prepend the implementation plan, the user's original request, what you were trying to do, or any explanation of intent.

**The prompt to send via the `Task` tool's `prompt` parameter is exactly the body delimited by `<<<TEMPLATE_START>>>` (exclusive) and `<<<TEMPLATE_END>>>` (exclusive).**

```
<<<TEMPLATE_START>>>
Independent code review of the pending changes on this branch.

Run ALL of the following to capture every kind of pending change:
- `git status` 
- `git diff` 
- `git diff --cached` 
- `git diff main...HEAD` 
- `git log main..HEAD --oneline` 

Also `git ls-files --others --exclude-standard` to find untracked new files. Read the touched files in full where the diff context is not enough.

Find substantive issues. For each finding: cite file:line, name the issue, explain WHY it is a bug or risk (not just what the code does), and suggest a concrete fix. Be specific.

Hunt for:
- Bugs: off-by-ones, null/undefined dereference, wrong variable used, etc.
- Security: injection, XSS, missing auth checks, IDOR.
- Race conditions: shared state without locks, async ordering, TOCTOU.
- Edge cases: empty arrays, NaN, Infinity, negative numbers.
- Error handling: silent catches, swallowed errors.
- Performance: N+1 queries, sync work in hot loops.
- Test coverage gaps: code paths not covered.
[BOOTSTRAP: stack-specific Hunt for items go here as additional bullets]
- Project-rule violations from AGENTS.md / CLAUDE.md (cite the relevant section).
- Dead code.

Do NOT surface:
- Stylistic preferences (formatting, naming, ordering)
- Micro-refactors that do not fix a bug
- Speculative concerns without a concrete failure mode

[NO ADDITIONAL FOCUS]

Output format: numbered list. For each finding, lead with `file:line` then the issue and fix. End the response with the literal string `no findings` if (and only if) the diff is clean.
<<<TEMPLATE_END>>>
```

If the user passed a focus area as the skill argument (e.g. `/eg-precommit-review "auth flow"`), replace `[NO ADDITIONAL FOCUS]` with:

```
ADDITIONAL FOCUS: <user-supplied focus area, verbatim>. Spend extra attention here, but still surface anything else substantive you find.
```

## Step 3: Triage the findings

For each finding the reviewer returns:
- **Fix it** — apply the change using `StrReplace` or `Write`.
- **Rebut it** — write a one-line reason. Examples: "False positive: the value cannot be null here because <X>", "Out of scope for this diff; tracked as follow-up <Y>", "Intentional: see AGENTS.md §Z".

**Surface every rebuttal back to the user verbatim** in the final report. The user — not the reviewer — has the final say on rebuttals.

## Step 4: Maintain a ledger and re-invoke

Before re-invoking, print to the user:

```
Open findings going into round N:
- [from round 1] file:line — fixed (commit not yet made; in-flight)
- [from round 1] file:line — rebutted: <verbatim reason>
[...]
```

Then re-invoke the reviewer using the `Task` tool. Re-include the FULL original template body, then this addendum:

```
Previous round's fixes:
- file:line — what changed
[...]

Verify each fix is correct and complete. Look for anything you missed in the first pass, especially issues introduced by the fixes themselves.
```

## Step 5: Loop with hard cap

Repeat steps 3-4 until the reviewer returns the literal string `no findings` AND every prior-round finding is fixed-or-rebutted.

**Hard cap: 5 rounds.** Stop if (a) you hit 5 rounds without exiting, or (b) any new finding lands at the same `file:method` as a previous fix (a sign of churn rather than convergence).

When tripped, print a brief of open findings, then call `AskQuestion`:
- `prompt`: "Review hit the 5-round cap with N findings still open. What do you want to do?"
- `options`:
  1. **Accept and commit** — "Findings are acknowledged but I want to ship."
  2. **Keep working on fixes** — "Continue past the cap, override the safety stop."
  3. **Abandon the change** — "Roll back; not worth the risk."

## Step 6: Final report

Once the loop exits, print to the user:
- Rounds run
- Findings fixed (with file:line each)
- Findings rebutted (verbatim — every rebuttal must appear)
- Whether any pre-existing lint/typecheck/test errors were noted as out-of-scope
- Pre-flight gate status (lint / typecheck / unit / e2e / codegen)

**STOP at this step.** Do NOT commit. Wait for the user's literal commit instruction. [BOOTSTRAP: commit policy reminder]
