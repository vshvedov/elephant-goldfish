---
name: eg-new-feature
description: Build a new feature using the elephant/goldfish workflow — design doc, goldfish design check, implement, review, validate.
---

Build a new feature using the elephant/goldfish workflow. The aim: design before code, let a fresh goldfish stress-test the design doc, then implement, review, and validate.

If the user gave a GitHub issue URL or `#<number>`, fetch it with `run_shell_command` using `gh issue view <number> --json title,body,labels,comments` and seed the design doc from it.

[BOOTSTRAP: project-specific routing note]

## Step 0: Confirm scope before designing

Restate the request back to the user in 1-2 sentences ("I read this as: <X>. Confirm or correct.").

[BOOTSTRAP: project-priority sanity-check block]

[BOOTSTRAP: surface-area sanity-check]

## Step 1: Write the design doc

Print the design doc to the user. For substantial features, propose writing it to `[BOOTSTRAP: docs path]` using `write_file` and ask the user before creating the file.

Required sections:

```
DESIGN DOC
- Why: <user problem this solves; cite GH issue, conversation, or PRD section>
- Scope: <what is in; what is explicitly out>
- Surfaces touched: <files / routes / models / controllers / components / DB tables / external services>
- Interfaces: <component props, function signatures, API request/response shapes, DB columns, queue arguments>
- UX flow: <click-by-click for UI; request-by-request for backend>
[BOOTSTRAP: stack-specific design-doc fields]
- Failure modes: <what the user sees when each thing breaks; what the API returns>
- Verification criteria: <unit tests, E2E spec, manual steps>
- Out-of-scope follow-ups: <noted, not built>
```

[BOOTSTRAP: PRD reference note]

For UI work, sketch the visual structure in plain text or pseudo-JSX.

## Step 2: Goldfish design check

Spawn a fresh agent using `invoke_agent` (`agent_name="generalist"`):

The goldfish gets ONLY the design doc (no chat history, no implementation intent). Its job is to find holes in the doc — not to implement.

**Prompt body to send (between markers, exclusive):**

```
<<<DESIGN_START>>>
You are a fresh reviewer with no prior context. Below is a design doc for a feature in the [BOOTSTRAP: project name + one-sentence description] repo (GEMINI.md at the repo root has the architecture).

Your job: read the design doc, then read the surfaces it claims to touch, and find holes BEFORE implementation starts. Specifically:

- Is the scope crisp?
- Are the interfaces concrete enough?
- Do the verification criteria actually verify the feature?
- Does the doc misunderstand any existing code? Look up the surfaces it claims to touch and check.
- Are there failure modes the doc missed?
[BOOTSTRAP: stack-specific gap items]
- Are there project-specific gotchas the doc ignores? GEMINI.md is your reference.

[BOOTSTRAP: PRD note]

DESIGN DOC:

<PASTE FULL DESIGN DOC FROM STEP 1 HERE>

Output: numbered list of gaps, with file:line citations where applicable. End with `design ready` ONLY if you have zero gaps. Otherwise list them and end with `design needs revision`.
<<<DESIGN_END>>>
```

**Triage the gaps.** Each gap is either: addressed in a doc revision, or rebutted with a verbatim reason citing GEMINI.md or the user's words. Print the revised doc back to the user once gaps are closed.

If the goldfish flags real gaps three times in a row, the feature is under-specified — **stop and ask the user** for more direction via `ask_user`.

## Step 3: Implementation plan

Once the design doc is `design ready`, write a short ordered implementation plan in chat:

[BOOTSTRAP: implementation layer ordering for this stack.]

For trivial features (single-component change), skip this step.

## Step 4: Implement

Follow the plan using `replace`, `write_file`, and `run_shell_command`. After each layer, briefly verify before moving on:

[BOOTSTRAP: per-layer verification examples for this stack.]

[BOOTSTRAP: UI driving rule]

[BOOTSTRAP: cross-tenant or other always-verify reminder]

## Step 5: Hand off to review

Run the `eg-precommit-review` skill workflow explicitly if the user wants it, or carefully review your own diff.

## Step 6: Test gate

```sh
[BOOTSTRAP: test gate commands per stack]
```

All required tiers must pass. For UI features, also do a final walkthrough of the golden path AND the most plausible edge case.

## Step 7: Final report

Print to the user:
- Feature summary (one line)
- Files touched
- Tests added
- Design-check result (gaps surfaced and how each was resolved)
- Test gate status
- Out-of-scope follow-ups noted in the design doc

**STOP.** Do NOT commit. Wait for the user's literal commit instruction. [BOOTSTRAP: commit-policy reminder per project.]