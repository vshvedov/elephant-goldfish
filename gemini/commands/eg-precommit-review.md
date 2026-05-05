---
name: eg-precommit-review
description: Run the pre-commit independent-reviewer loop on the current branch's pending changes.
---

Run the pre-commit review loop. The goal: validate the pending changes locally before commit, with the rigor of an independent code review.

## Step 0: Decide whether to run

**Skip the loop for:** pure documentation-only commits (no code touched), single-line typo fixes, version bumps, dependency updates with no code changes, formatter-only diffs, merge commits.

**Run it for everything else.**

## Step 1: Pre-flight (sequentially, NOT chained with `&&`)

Execute these using `run_shell_command`:

```sh
[BOOTSTRAP: lint command]
```
- New errors introduced by the diff are blockers.

[BOOTSTRAP: typecheck block]
```sh
[BOOTSTRAP: typecheck command]
```

```sh
[BOOTSTRAP: unit test command]
```
- If a test fails because your implementation legitimately changed its expected behavior, do NOT rewrite the test silently.

[BOOTSTRAP: e2e test block]
```sh
[BOOTSTRAP: e2e test command]
```

[BOOTSTRAP: code-generation block]
```sh
[BOOTSTRAP: codegen command]
```

## Step 2: Spawn a fresh independent reviewer

Use `invoke_agent` with:
- `agent_name: "generalist"`

The reviewer must have NO implementation context — that asymmetry is what makes the review effective.

**Pass the prompt EXACTLY.** Do NOT prepend the implementation plan, the user's original request, what you were trying to do, or any explanation of intent.

**The prompt to send to `invoke_agent` is exactly the body delimited by `<<<TEMPLATE_START>>>` (exclusive) and `<<<TEMPLATE_END>>>` (exclusive).**

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
- Project-rule violations from GEMINI.md (cite the relevant section).
- Dead code.

Do NOT surface:
- Stylistic preferences (formatting, naming, ordering)
- Micro-refactors that do not fix a bug
- Speculative concerns without a concrete failure mode

[NO ADDITIONAL FOCUS]

Output format: numbered list. For each finding, lead with `file:line` then the issue and fix. End the response with the literal string `no findings` if (and only if) the diff is clean.
<<<TEMPLATE_END>>>
```

## Step 3: Triage the findings

For each finding the reviewer returns:
- **Fix it** — apply the change using `replace` or `write_file`.
- **Rebut it** — write a one-line reason. 

**Surface every rebuttal back to the user verbatim** in the final report. 

## Step 4: Maintain a ledger and re-invoke

Before re-invoking, print to the user:
```
Open findings going into round N:
- [from round 1] file:line — fixed (commit not yet made; in-flight)
- [from round 1] file:line — rebutted: <verbatim reason>
[...]
```

Then re-invoke using `invoke_agent`. Re-include the FULL original template body, then this addendum:

```
Previous round's fixes:
- file:line — what changed
[...]

Verify each fix is correct and complete. Look for anything you missed in the first pass, especially issues introduced by the fixes themselves.
```

## Step 5: Loop with hard cap

Repeat steps 3-4 until the reviewer returns the literal string `no findings` AND every prior-round finding is fixed-or-rebutted.

**Hard cap: 5 rounds.** Stop if (a) you hit 5 rounds without exiting, or (b) any new finding lands at the same `file:method` as a previous fix.

When tripped, print a brief of open findings, then call `ask_user`:
- `question`: "Review hit the 5-round cap with N findings still open. What do you want to do?"
- `header`: `"R5 cap"`
- `multiSelect`: `false`
- `options`:
  1. **Accept and commit** 
  2. **Keep working on fixes** 
  3. **Abandon the change** 

## Step 6: Final report

Once the loop exits, print to the user:
- Rounds run
- Findings fixed (with file:line each)
- Findings rebutted (verbatim)
- Whether any pre-existing lint/typecheck/test errors were noted as out-of-scope

**STOP at this step.** Do NOT commit. Wait for the user's literal commit instruction. [BOOTSTRAP: commit policy reminder]