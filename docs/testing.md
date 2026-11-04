# Testing the harness

The product is prompts. Passing a YAML check doesn't prove an agent follows them.

## Offline checks

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
git diff --check
```

The suite checks all 30 skill files, metadata, bootstrap inventories, cross-workflow
references and recovery/dispatch contracts. Git fixtures demonstrate a staged bug
hidden by the working copy, Unicode untracked paths and content changes invisible
to status. These are structural and fixture tests, not simulated model approvals.

## Native checks

Use disposable repos and retain transcripts outside this repository. Never run
behavioral fixtures against an actual project with pending work. Record the host
version, skill revision, input, observed tool calls, output and source/index/HEAD
snapshots. A blocked login or missing tool is unverified, not a pass.

For Grok, copy `grok/skills/` into the fixture's `.grok/skills/`, run
`grok --trust --cwd <fixture> inspect --json` (trusting only that disposable
fixture), and confirm all six discovered paths point to that fixture.
Run a question about the fixture with `/eg-question`. Check for fresh `task` calls,
cited answers and unchanged source/index/HEAD. Review child dispatch arguments;
a final answer saying it used readers is not enough evidence.

For Claude, copy `claude/commands/` into `.claude/commands/` in the fixture and invoke
the relevant command. For Codex, use a disposable project's skill loading surface
and verify that it loaded the candidate rather than a user's installed version.
Cursor and Gemini require their own native runs before claiming behavioral parity.

## Behavior scenarios

Each row needs an actual host trace or is recorded as unverified. Use one fresh
session per scenario; don't add the expected answer to the agent's input.

| Scenario | Expected observation |
|---|---|
| Question about a code path | Fresh readers, file:line citations, no source writes or ledger. |
| Staged reversal plus untracked bug | Review identifies the index bug and untracked defect; no clean claim from combined diff. |
| Reviewer cannot read a patch | Incomplete, not no findings. |
| Untracked contents change mid-review | Snapshot invalidated even when filenames/status are unchanged. |
| Standing rebuttal repeated without evidence | Rebuttal retained and reported verbatim, no infinite reopen loop. |
| T2 depends on unfinished T1 | Task stops before design/implementation. |
| Duplicate IDs, missing fields or dependency cycle | Explicit malformed-roadmap report, no fabricated task. |
| PRD changes during implementation | No stale Status overwrite; reconcile with user. |
| Task succeeds but status isn't saved | Suggest next task provisionally and warn the next session sees old status. |
| Compaction during review | Read exact ledger and current skill; verify evidence freshness before resuming. |
| Trivial edit | Edit actually applied before skipping diagnosis. |
| Generation-input change | Generate before dependent checks. |
| Lightweight PRD with web selected | No deep research wave. |
| Update has local edits and incomplete download | Existing install untouched; no partial replacement. |

Review scope should include both the new prompts and existing host integration.
Keep unexecuted rows visible in release notes rather than calling the full harness
validated from one smoke test.

## Validation on 2026-11-04

- Offline suite: 9 tests passed, covering the 30 workflow files and two real Git
  fixtures. A clean virtual environment installed the documented dependency.
- Grok Build 1.0.50: trusted-fixture discovery found all six native project skills.
  A live `eg-question` run used two fresh `spawn_subagent` calls, returned code
  citations, and left source, index, HEAD and the fixture's file inventory unchanged.
  The exposed tool schema differed from the static `task` name; the adapter now
  explicitly follows whichever native schema is exposed.
- Claude Code 2.1.289: the installed command expanded in the native transcript.
  A live precommit review dispatched a fresh reader, found both the staged reversal
  and untracked conversion bug, and preserved source/index/HEAD. The private parent
  marker was absent from child dispatch. Separate staged-candidate tests were
  deliberately not run and the report did not claim a clean result.
- Claude PRD task check: T2 with unfinished prerequisite T1 stopped before design
  or implementation. All fixture files were unchanged.
- Two independent code-review rounds: fixed review-only generation isolation and
  rollback of transaction-created files. The final round had no findings.

Native Cursor, Gemini and Codex behavior was not exercised for this revision.
The remaining scenario rows above, including actual compaction, upgrade rollback
failure and concurrent PRD edits, are unverified. The checks do not establish
complete behavioral coverage of every workflow or host.
